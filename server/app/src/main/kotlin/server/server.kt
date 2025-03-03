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
import openai.getCompletionResponse

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

        // Define the routing
    routing {
        // Serve static files from the frontend/build directory
        singlePageApplication {
            react("/home/kiz/app/frontend/build")
        }

        post("/completion") {
            try {
                val rawBody = call.receiveText()
                print("Raw request body: $rawBody")
                val request =
                    kotlinx.serialization.json.Json.decodeFromString<CompletionRequest>(rawBody) // Parse incoming JSON
                val response = generateCompletion(request)
                println("Response $response")

                // Send the response as JSON
                call.respond(response)
            } catch (e: Exception) {
                print("Exception: $e")
                call.respond(CompletionResponse(completion = "fail"))
            }
        }
    }
}

// Function to generate a dummy response for completion
fun generateCompletion(request: CompletionRequest): CompletionResponse {
    val completion = getCompletionResponse(request.content)
    return CompletionResponse(
        completion = completion
    )
}

// DTOs for request and response

@Serializable
data class CompletionRequest(
    val content: String
)

@Serializable
data class CompletionResponse(
    val completion: String
)