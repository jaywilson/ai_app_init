package openai

import io.ktor.client.*
import io.ktor.client.engine.cio.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.http.*
import io.ktor.client.plugins.contentnegotiation.*
import kotlinx.coroutines.runBlocking
import io.ktor.serialization.kotlinx.json.*
import server.CompletionRequest


fun getCompletionResponse(content: String): String {
    // Run the HTTP POST request in a coroutine
    print("Here")
    return runBlocking {
        print("In run blocking")
        // Create an HTTP client
        val client = HttpClient(CIO) {
            install(ContentNegotiation) {
                json() // Add JSON serialization support
            }
        }

        // Define the endpoint URL
        val url = "http://localhost:9002/completion"

        // Define the request body
        val requestBody = CompletionRequest(
            content = content
        )

        print("about to try for response")

        client.use { c ->
            // Send the POST request
            val response: HttpResponse = c.post(url) {
                contentType(ContentType.Application.Json) // Set Content-Type to JSON
                setBody(requestBody)                     // Set the request body as JSON
            }
            print("got a response")
            response.bodyAsText()
        }
    }
}