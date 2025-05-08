package com.proxym.amir.clickup_ticket_service.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter 
@Setter
@NoArgsConstructor
public class ClickUpTicketRequest {

    @NotBlank(message = "Ticket name cannot be blank")
    @Size(max = 250 , message = "Ticket name cannot exceed 250 Characters ")
    private String name;

    private String description;

    @Min(value = 1, message = "Priority must be between 1 (Urgent) and 4 (Low)")
    @Max(value = 4, message = "Priority must be between 1 (Urgent) and 4 (Low)")
    private Integer priority = 3  ; 

    private String status = "To Do";

}
