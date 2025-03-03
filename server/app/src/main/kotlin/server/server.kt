package server

import io.ktor.server.application.*
import io.ktor.http.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import kotlinx.serialization.Serializable
import io.ktor.server.plugins.contentnegotiation.*
import io.ktor.serialization.kotlinx.json.*
import openai.getCompletionResponse

fun main() {
    // Set up and start the Ktor server
    embeddedServer(Netty, port = 8080, host = "0.0.0.0") {
        module()
    }.start(wait = true)
}

fun Application.module() {
    // Enable JSON serialization with ktor
    install(ContentNegotiation) {
        json()
    }

    // Define the routing
    routing {
        post("/completion") {
            val request = call.receive<CompletionRequest>() // Parse incoming JSON
            val response = generateCompletion(request)

            // Send the response as JSON
            call.respond(response)
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