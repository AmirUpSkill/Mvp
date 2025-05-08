package com.proxym.amir.clickup_ticket_service.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class ClickUpTaskResponse {

    private String message ; 

    @JsonProperty("task_id")
    private String taskId ; 

    private String url;

    
}
