package server

import io.ktor.server.application.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import kotlinx.serialization.Serializable
import io.ktor.server.plugins.contentnegotiation.*
import io.ktor.serialization.kotlinx.json.*
import io.ktor.server.http.content.*
import openai.getProjectResponse
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.storage.blob.BlobServiceClientBuilder;
import io.ktor.http.*

class MainApp {
    companion object {
        @JvmStatic
        fun main(args: Array<String>) {
            // Set up and start the Ktor server
            embeddedServer(Netty, port = 8080, host = "0.0.0.0") {
                module()
            }.start(wait = true)
        }
    }
}

fun Application.module() {
    // Enable JSON serialization with ktor
    install(ContentNegotiation) {
        json()
    }

    val blobServiceClient = BlobServiceClientBuilder()
        .endpoint("https://kizarastore.blob.core.windows.net")
        .credential(DefaultAzureCredentialBuilder().build())
        .buildClient()
    val containerClient = blobServiceClient.getBlobContainerClient("app")

        // Define the routing
    routing {
        // Serve static files from the frontend/build directory
        singlePageApplication {
            react("/home/kiz/app/frontend/build")
        }

        post("/frontend_project") {
            try {
                print("REQUEST frontend_project")
                val request = call.receive<ProjectRequest>()
                val response = getProjectResponse(request.content)
                call.respond(response)
            } catch (e: Exception) {
                print("Exception: $e")
                call.respond(ProjectResponse(error = e.message))
            }
        }

        get("/download_project") {
            try {
                val projectId = call.parameters["project_id"]
                print("REQUEST download_project?project_id=$projectId")
                val blobClient = containerClient.getBlobClient("${projectId}/project.zip")
                val zipContents = blobClient.downloadContent().toBytes()

                call.response.header("Content-Disposition", "attachment; filename=\"project.zip\"")
                call.respondBytes(zipContents, contentType = ContentType.Application.Zip)
            } catch (e: Exception) {
                print("Exception: $e") 
                call.respond(ProjectResponse(error = e.message))
            }
        }   
    }
}

// DTOs for request and response

@Serializable
data class ProjectRequest(
    val content: String
)

@Serializable
data class ProjectResponse(
    val projectId: String? = null,
    val error: String? = null
)