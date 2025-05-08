package com.amir.api_gateway_service.filter;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cloud.gateway.filter.GatewayFilter;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.core.Ordered;
import org.springframework.http.HttpHeaders;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

@Component
public class ForwardAuthHeaderFilter implements GatewayFilter, Ordered {

    private static final Logger logger = LoggerFactory.getLogger(ForwardAuthHeaderFilter.class);
    private static final String AUTHORIZATION_HEADER = HttpHeaders.AUTHORIZATION;
    private static final String BEARER_PREFIX = "Bearer ";

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        HttpHeaders headers = request.getHeaders();

        if (headers.containsKey(AUTHORIZATION_HEADER)) {
            String authHeader = headers.getFirst(AUTHORIZATION_HEADER);
            if (authHeader != null && authHeader.startsWith(BEARER_PREFIX)) {
                logger.debug("Authorization Bearer header found. Forwarding to downstream service for path: {}", request.getPath());

                ServerHttpRequest modifiedRequest = request.mutate()
                        .header(AUTHORIZATION_HEADER, authHeader)
                        .build();

                ServerWebExchange modifiedExchange = exchange.mutate().request(modifiedRequest).build();

                return chain.filter(modifiedExchange);
            } else {
                logger.debug("Authorization header found but is not a Bearer token. Proceeding without forwarding for path: {}", request.getPath());
            }
        } else {
            logger.debug("No Authorization header found. Proceeding without forwarding for path: {}", request.getPath());
        }

        return chain.filter(exchange);
    }

    @Override
    public int getOrder() {
        return 1;
    }
}