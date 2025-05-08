package com.proxym.amir.clickup_ticket_service.client;

import com.proxym.amir.clickup_ticket_service.config.ClickUpProperties;
import com.proxym.amir.clickup_ticket_service.dto.ClickUpTicketRequest;
import com.proxym.amir.clickup_ticket_service.exception.ClickUpApiException; // Import the custom exception
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatusCode; // Import HttpStatusCode
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.ClientResponse; // Import ClientResponse
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Component
@RequiredArgsConstructor
@Slf4j
public class ClickUpApiClient {

    private final WebClient clickUpWebClient;
    private final ClickUpProperties clickUpProperties;

    /**
     * Sends a request to create a new task in ClickUp.
     *
     * @param ticketRequest The details of the ticket to create.
     * @return A Mono emitting the ClickUp API response upon success, or signaling a ClickUpApiException on failure.
     */
    public Mono<ClickUpApiTaskCreateResponse> createClickUpTask(ClickUpTicketRequest ticketRequest) {
        String specificListUri = String.format("/list/%s/task", clickUpProperties.getListId());

        // Consider using structured logging or masking sensitive data in production
        log.debug("Sending request to ClickUp API: URI={}, PayloadName={}", specificListUri, ticketRequest.getName());

        return clickUpWebClient.post()
                .uri(specificListUri)
                .bodyValue(ticketRequest) // Send the DTO as the request body
                .retrieve() // Retrieve the response
                // --- Corrected Error Handling ---
                .onStatus(
                        HttpStatusCode::isError, // Use method reference for conciseness
                        this::handleClickUpError // Extract error handling to a separate method
                )
                // --- Success Handling ---
                .bodyToMono(ClickUpApiTaskCreateResponse.class) // Deserialize success response
                .doOnSuccess(response -> {
                    // Add null check for safety
                    if (response != null && response.getId() != null) {
                        log.info("Successfully created ClickUp task: ID={}", response.getId());
                    } else {
                        log.warn("ClickUp task creation reported success, but response or ID is null. Response: {}", response);
                    }
                })
                // Log errors more specifically
                .doOnError(ClickUpApiException.class, error ->
                        log.error("ClickUp API call failed with status {}: {}", error.getStatusCode(), error.getMessage()))
                .doOnError(error -> !(error instanceof ClickUpApiException), error ->
                        log.error("Error processing ClickUp API call (non-API error)", error));
    }

    /**
     * Handles error responses (4xx or 5xx) from the ClickUp API.
     * Reads the error body and returns a Mono signaling a ClickUpApiException.
     *
     * @param clientResponse The error ClientResponse from WebClient.
     * @return A Mono containing the ClickUpApiException.
     */
    private Mono<Throwable> handleClickUpError(ClientResponse clientResponse) {
        // Try to read the error body as a String
        return clientResponse.bodyToMono(String.class)
                // If body is empty, provide a default message
                .defaultIfEmpty("{ \"error\": \"No error body provided by ClickUp\" }")
                // Create the exception within a flatMap (since Mono.error returns Mono<Throwable>)
                .flatMap(errorBody -> {
                    log.error("ClickUp API error: Status={}, Body={}", clientResponse.statusCode(), errorBody);
                    String errorMessage = "Failed to process ClickUp request. Status: " + clientResponse.statusCode() + ". Response: " + errorBody;
                    // Return the Mono signalling the error
                    return Mono.error(new ClickUpApiException(errorMessage, clientResponse.statusCode()));
                });
    }

    /**
     * Inner DTO class representing the expected successful JSON response structure from the ClickUp "Create Task" API endpoint.
     * Consider moving this to its own file in a 'client.dto' sub-package for better organization.
     */
    @lombok.Data // Includes @Getter, @Setter, @ToString, @EqualsAndHashCode, @RequiredArgsConstructor
    public static class ClickUpApiTaskCreateResponse {
        private String id;
        private String url;
        // Add any other fields returned by ClickUp API that you might need.
    }
}