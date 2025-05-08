package com.proxym.amir.clickup_ticket_service.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.proxym.amir.clickup_ticket_service.dto.ClickUpTaskResponse;
import com.proxym.amir.clickup_ticket_service.dto.ClickUpTicketRequest;
import com.proxym.amir.clickup_ticket_service.service.ClickUpTicketService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.annotation.AuthenticationPrincipal;

/**
 * REST Controller for handling ClickUp ticket operations
 */
@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
@Slf4j
public class ClickUpTicketController {

    private final ClickUpTicketService clickUpTicketService;

    /**
     * Creates a new ticket in ClickUp
     * @param ticketRequest The ticket details
     * @param jwtPrincipal The authenticated user's JWT
     * @return The created ticket response
     */
    @PostMapping("/create-ticket")
    public ResponseEntity<ClickUpTaskResponse> createTicket(
            @RequestBody @Valid ClickUpTicketRequest ticketRequest,
            @AuthenticationPrincipal Jwt jwtPrincipal
    ) {
        String userIdentifier = jwtPrincipal.getClaimAsString("email") != null ?
                               jwtPrincipal.getClaimAsString("email") :
                               jwtPrincipal.getSubject();
        log.info("User '{}' requested to create ticket: {}", userIdentifier, ticketRequest.getName());

        ClickUpTaskResponse response = clickUpTicketService.createTicket(ticketRequest);

        log.info("Successfully processed create ticket request for user '{}', TaskID='{}'",
                 userIdentifier, response.getTaskId());

        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * Health check endpoint
     * @return Status of the service
     */
    @GetMapping("/health")
    public ResponseEntity<String> healthCheck() {
        return ResponseEntity.ok("{\"status\": \"UP\"}");
    }
}