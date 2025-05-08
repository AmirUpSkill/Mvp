package com.proxym.amir.clickup_ticket_service.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.oauth2.jose.jws.MacAlgorithm;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder;
import org.springframework.security.web.SecurityFilterChain;

import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    @Value("${jwt.secret}")
    private String jwtSecretKey;

    @Value("${jwt.issuer}")
    private String jwtIssuer;

    @Bean
    public JwtDecoder jwtDecoder() {
        if (jwtSecretKey == null || jwtSecretKey.isBlank()) {
            throw new IllegalStateException("JWT secret key ('jwt.secret') is not configured in application properties.");
        }

        SecretKeySpec secretKey = new SecretKeySpec(jwtSecretKey.getBytes(StandardCharsets.UTF_8), "HmacSHA512");

        NimbusJwtDecoder decoder = NimbusJwtDecoder.withSecretKey(secretKey)
               .macAlgorithm(MacAlgorithm.HS512)
               .build();

        return decoder;
    }

   @Bean
   public SecurityFilterChain securityFilterChain(HttpSecurity http, JwtDecoder jwtDecoder) throws Exception {
       http
           .csrf(AbstractHttpConfigurer::disable)
           .authorizeHttpRequests(auth -> auth
               .requestMatchers("/api/v1/health").permitAll()
               .anyRequest().authenticated()
           )
           .oauth2ResourceServer(oauth2 -> oauth2
               .jwt(jwt -> jwt.decoder(jwtDecoder))
           )
           .sessionManagement(session -> session
               .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
           );

       return http.build();
   }
}