package com.proxym.amir.clickup_ticket_service.exception;

import lombok.Getter;
import org.springframework.http.HttpStatusCode;

/**
 * Custom exception for errors occurring during interaction with the ClickUp API.
 */
@Getter // Automatically generates getter for statusCode
public class ClickUpApiException extends RuntimeException {

    private final HttpStatusCode statusCode;

    /**
     * Constructs a new ClickUpApiException with the specified detail message and status code.
     *
     * @param message    The detail message.
     * @param statusCode The HTTP status code received from ClickUp or relevant to the error.
     */
    public ClickUpApiException(String message, HttpStatusCode statusCode) {
        super(message);
        this.statusCode = statusCode;
    }

    /**
     * Constructs a new ClickUpApiException with the specified detail message, status code, and cause.
     *
     * @param message    The detail message.
     * @param statusCode The HTTP status code received from ClickUp or relevant to the error.
     * @param cause      The cause (which is saved for later retrieval by the getCause() method).
     */
    public ClickUpApiException(String message, HttpStatusCode statusCode, Throwable cause) {
        super(message, cause);
        this.statusCode = statusCode;
    }
}