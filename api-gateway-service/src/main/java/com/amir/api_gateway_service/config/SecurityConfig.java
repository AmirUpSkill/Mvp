package com.amir.api_gateway_service.config;

import com.amir.api_gateway_service.security.CustomOAuth2SuccessHandler;
import org.springframework.security.oauth2.jose.jws.MacAlgorithm;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.reactive.EnableWebFluxSecurity;
import org.springframework.security.config.web.server.ServerHttpSecurity;
import org.springframework.security.oauth2.jwt.NimbusReactiveJwtDecoder;
import org.springframework.security.oauth2.jwt.ReactiveJwtDecoder;
import org.springframework.security.web.server.SecurityWebFilterChain;

import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;

@Configuration
@EnableWebFluxSecurity
public class SecurityConfig {

    private final CustomOAuth2SuccessHandler customOAuth2SuccessHandler;
    private final JwtProperties jwtProperties;

    public SecurityConfig(CustomOAuth2SuccessHandler customOAuth2SuccessHandler,
                          JwtProperties jwtProperties) {
        this.customOAuth2SuccessHandler = customOAuth2SuccessHandler;
        this.jwtProperties = jwtProperties;
    }

    @Bean
    public SecurityWebFilterChain springSecurityFilterChain(ServerHttpSecurity http) {
        http
            .csrf(ServerHttpSecurity.CsrfSpec::disable)
            .authorizeExchange(exchanges -> exchanges
                .pathMatchers("/login/**", "/oauth2/**", "/error").permitAll()
                .pathMatchers("/actuator/health").permitAll()
                .pathMatchers("/gw/me").authenticated()
                .anyExchange().authenticated()
            )
            .oauth2Login(oauth2 -> oauth2
                .authenticationSuccessHandler(customOAuth2SuccessHandler)
            )
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(jwt -> jwt
                    .jwtDecoder(customJwtDecoder())
                )
            )
            .logout(Customizer.withDefaults());

        return http.build();
    }

    @Bean
    public ReactiveJwtDecoder customJwtDecoder() {
        String secret = jwtProperties.getSecret();
        SecretKeySpec secretKey = new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA512");
        return NimbusReactiveJwtDecoder.withSecretKey(secretKey)
               .macAlgorithm(MacAlgorithm.HS512)
               .build();
    }
}