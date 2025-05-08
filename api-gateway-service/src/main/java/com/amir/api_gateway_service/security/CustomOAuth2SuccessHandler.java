package com.amir.api_gateway_service.security; 

import com.amir.api_gateway_service.config.JwtProperties;
import com.amir.api_gateway_service.security.jwt.JwtTokenProvider;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.server.WebFilterExchange;
import org.springframework.security.web.server.authentication.ServerAuthenticationSuccessHandler;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.net.URI;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

@Component
public class CustomOAuth2SuccessHandler implements ServerAuthenticationSuccessHandler {

    private static final Logger logger = LoggerFactory.getLogger(CustomOAuth2SuccessHandler.class);

    private final JwtTokenProvider jwtTokenProvider;
    private final JwtProperties jwtProperties; // To get the redirect URI

    public CustomOAuth2SuccessHandler(JwtTokenProvider jwtTokenProvider, JwtProperties jwtProperties) {
        this.jwtTokenProvider = jwtTokenProvider;
        this.jwtProperties = jwtProperties;
        logger.info("CustomOAuth2SuccessHandler initialized with redirect URI: {}", jwtProperties.getFrontendLoginSuccessRedirectUri());
    }

    @Override
    public Mono<Void> onAuthenticationSuccess(WebFilterExchange webFilterExchange, Authentication authentication) {
        ServerWebExchange exchange = webFilterExchange.getExchange();
        OAuth2User oauth2User = (OAuth2User) authentication.getPrincipal();

        if (oauth2User == null) {
            logger.error("OAuth2User principal is null after successful authentication. Cannot generate JWT.");
            // Handle error appropriately - perhaps redirect to an error page
            exchange.getResponse().setStatusCode(HttpStatus.INTERNAL_SERVER_ERROR);
            return exchange.getResponse().setComplete();
        }

        logger.info("OAuth2 authentication successful for user: {}", oauth2User.getName());

        // 1. Generate JWT token using the JwtTokenProvider
        String jwtToken = jwtTokenProvider.generateToken(oauth2User);
        logger.debug("Generated JWT for user {}: [JWT_REDACTED_FOR_LOG]", oauth2User.getName());


        // 2. Construct the redirect URI with the token in the fragment
        //    Example: http://localhost:3000/auth/callback#access_token=YOUR_JWT_HERE
        String baseRedirectUri = jwtProperties.getFrontendLoginSuccessRedirectUri();
        String tokenFragment = "access_token=" + URLEncoder.encode(jwtToken, StandardCharsets.UTF_8);
        String finalRedirectUri = baseRedirectUri + "#" + tokenFragment;

        logger.info("Redirecting user to frontend with JWT in fragment: {}", baseRedirectUri + "#access_token=[REDACTED]");


        // 3. Perform the redirect
        exchange.getResponse().setStatusCode(HttpStatus.FOUND); // 302 Redirect
        exchange.getResponse().getHeaders().setLocation(URI.create(finalRedirectUri));

        // Indicate that the response is handled and complete
        return exchange.getResponse().setComplete();
    }
}