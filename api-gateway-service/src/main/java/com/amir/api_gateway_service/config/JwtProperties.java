package com.amir.api_gateway_service.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import org.springframework.validation.annotation.Validated;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Positive;
import lombok.Getter;
import lombok.Setter;

@Configuration
@ConfigurationProperties(prefix = "jwt")
@Getter
@Setter
@Validated
public class JwtProperties {

    @NotBlank(message = "JWT secret key cannot be blank")
    private String secret;

    @Positive(message = "JWT expiration time must be positive")
    private long expirationMs;

    @NotBlank(message = "JWT issuer cannot be blank")
    private String issuer;

    @NotBlank(message = "Frontend redirect URL after successful login cannot be blank")
    private String frontendLoginSuccessRedirectUri;



}
