// Final Sketch - ClickUpTicketService.java
package com.proxym.amir.clickup_ticket_service.service;

import com.proxym.amir.clickup_ticket_service.client.ClickUpApiClient;
import com.proxym.amir.clickup_ticket_service.dto.ClickUpTicketRequest;
import com.proxym.amir.clickup_ticket_service.dto.ClickUpTaskResponse;
// Import the client's inner response DTO explicitly if not done already
import com.proxym.amir.clickup_ticket_service.client.ClickUpApiClient.ClickUpApiTaskCreateResponse;
import com.proxym.amir.clickup_ticket_service.exception.ClickUpApiException; // Import this too
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;
// Potentially add import for HttpStatusCode if needed for exception handling later

@Service
@RequiredArgsConstructor
@Slf4j
public class ClickUpTicketService {

    private final ClickUpApiClient clickUpApiClient;

    /**
     * Creates a ClickUp ticket using the provided request details.
     * Orchestrates the call to the ClickUpApiClient and maps the result.
     *
     * @param request The validated request DTO containing ticket details.
     * @return The response DTO containing the ID and URL of the created task.
     * @throws ClickUpApiException If the ClickUp API call fails.
     * @throws IllegalStateException If the ClickUp API call succeeds but returns an unexpected null response.
     */
    public ClickUpTaskResponse createTicket(ClickUpTicketRequest request) {
        log.info("Attempting to create ClickUp ticket with name: {}", request.getName());

        // Call the reactive client method
        Mono<ClickUpApiTaskCreateResponse> responseMono = clickUpApiClient.createClickUpTask(request);

        ClickUpApiTaskCreateResponse clientResponse = null;
        try {
            // Block to get the result synchronously.
            // Add .block(Duration) in production if needed.
            clientResponse = responseMono.block();
        } catch (ClickUpApiException e) {
            // Log the specific API exception caught from .block()
            log.error("Failed to create ticket via ClickUp API: {}", e.getMessage());
            // Re-throw the exception to be handled by the GlobalExceptionHandler
            throw e;
        } catch (Exception e) {
            // Catch other potential runtime exceptions from .block() (e.g., IllegalStateException if Mono terminates unexpectedly)
            log.error("An unexpected error occurred while waiting for ClickUp API response", e);
            // Wrap in a generic runtime exception or a specific internal service exception
            throw new RuntimeException("Internal error processing ClickUp request", e);
        }


        // Basic check for safety after blocking
        if (clientResponse == null || clientResponse.getId() == null) {
            log.error("Received null response or null ID from ClickUpApiClient despite reported success.");
            // Or throw a custom InternalServerErrorException
            throw new IllegalStateException("Received unexpected null response from ClickUp API client after successful call.");
        }

        // Map the successful client response to the API response DTO
        String message = "Ticket created successfully";
        ClickUpTaskResponse apiResponse = new ClickUpTaskResponse(
                message,
                clientResponse.getId(),
                clientResponse.getUrl()
        );

        log.info("Successfully created ClickUp ticket: ID={}, URL={}", apiResponse.getTaskId(), apiResponse.getUrl());
        return apiResponse;
    }
}