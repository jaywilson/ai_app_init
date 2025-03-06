package openai

import io.ktor.client.*
import io.ktor.client.engine.cio.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.http.*
import io.ktor.client.plugins.contentnegotiation.*
import kotlinx.coroutines.runBlocking
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.json.Json
import server.ProjectRequest
import server.ProjectResponse


fun getProjectResponse(content: String): ProjectResponse {
    return runBlocking {
        val client = HttpClient(CIO) {
            install(ContentNegotiation) {
                json()
            }
            engine {
                requestTimeout = 300000 // 300 sec
            }
        }

        val url = "http://localhost:9002/frontend_project"
        val requestBody = ProjectRequest(
            content = content
        )
        client.use { c ->
            val response: HttpResponse = c.post(url) {
                contentType(ContentType.Application.Json)
                setBody(requestBody)                   
            }
            Json.decodeFromString<ProjectResponse>(response.bodyAsText())
        }
    }
}