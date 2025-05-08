package com.amir.api_gateway_service;

import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.RestController;



@SpringBootApplication
@RestController
public class ApiGatewayServiceApplication {

    public static void main(String[] args) {
        org.springframework.boot.SpringApplication.run(ApiGatewayServiceApplication.class, args);
    }

}

