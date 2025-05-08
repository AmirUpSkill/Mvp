package com.amir.api_gateway_service.controller;

import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.web.bind.annotation.RestController;

import reactor.core.publisher.Mono;

@RestController
public class UserController {

    public Mono<Object> getMe(@AuthenticationPrincipal OAuth2User principal) {
       if (principal != null) {
          return Mono.just(principal.getAttributes());
      
        }
        return Mono.just("Not Authenticated");
    }

}
