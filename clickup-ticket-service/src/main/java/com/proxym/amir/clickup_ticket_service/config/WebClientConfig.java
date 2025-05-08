package com.proxym.amir.clickup_ticket_service.config;

import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
@RequiredArgsConstructor
public class WebClientConfig {

    private final ClickUpProperties clickUpProperties;

    @Bean
    public WebClient clickUpWebClient(WebClient.Builder builder) {
        return builder
                .baseUrl(clickUpProperties.getApiBaseUrl())
                .defaultHeader(HttpHeaders.AUTHORIZATION, clickUpProperties.getApiKey())
                .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                .build();
    }
}
