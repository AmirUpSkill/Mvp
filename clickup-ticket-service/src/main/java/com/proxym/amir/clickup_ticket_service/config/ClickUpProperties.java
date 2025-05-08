package com.proxym.amir.clickup_ticket_service.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import org.springframework.validation.annotation.Validated;

import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.Setter;

@Configuration
@ConfigurationProperties(prefix = "clickup")
@Getter
@Setter
@Validated
public class ClickUpProperties {

    @NotBlank(message = "ClickUp Api key must be configured ")
    private String apiKey; 
    @NotBlank(message = "ClickUp List ID must be configured")
    private String listId; 
    @NotBlank(message = "ClickUp Api Base Url must be configured")
    private String apiBaseUrl;



}
