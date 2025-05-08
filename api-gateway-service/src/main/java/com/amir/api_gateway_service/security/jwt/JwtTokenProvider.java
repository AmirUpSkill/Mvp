package com.amir.api_gateway_service.security.jwt;

import com.amir.api_gateway_service.config.JwtProperties;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;
import java.security.Key;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

@Component
public class JwtTokenProvider {

    private static final Logger logger = LoggerFactory.getLogger(JwtTokenProvider.class);

    private final Key signingKey;
    private final JwtProperties jwtProperties;
    private final SignatureAlgorithm signatureAlgorithm = SignatureAlgorithm.HS512;

    public JwtTokenProvider(JwtProperties jwtProperties) {
        this.jwtProperties = jwtProperties;
        byte[] keyBytes = jwtProperties.getSecret().getBytes(StandardCharsets.UTF_8);
        this.signingKey = Keys.hmacShaKeyFor(keyBytes);
        logger.info("JWT Signing Key initialized successfully using {} algorithm.", signatureAlgorithm.getValue());
    }

    public String generateToken(OAuth2User oauth2User) {
        String subject = oauth2User.getName();

        Date now = new Date();
        long expirationMillis = jwtProperties.getExpirationMs();
        Date validity = new Date(now.getTime() + expirationMillis);

        Map<String, Object> claims = new HashMap<>();
        String email = oauth2User.getAttribute("email");
        String name = oauth2User.getAttribute("name");
        String picture = oauth2User.getAttribute("picture");

        if (email != null) {
            claims.put("email", email);
        }
        if (name != null) {
            claims.put("name", name);
        }
        if (picture != null) {
            claims.put("picture", picture);
        }

        logger.debug("Generating JWT for user: '{}', with subject: '{}'", name, subject);
        logger.debug("Token will expire at: {}", validity);

        String token = Jwts.builder()
                .setSubject(subject)
                .setIssuer(jwtProperties.getIssuer())
                .setIssuedAt(now)
                .setExpiration(validity)
                .addClaims(claims)
                .signWith(signingKey, signatureAlgorithm)
                .compact();

        logger.info("Successfully generated JWT for user subject: {}", subject);

        return token;
    }
}