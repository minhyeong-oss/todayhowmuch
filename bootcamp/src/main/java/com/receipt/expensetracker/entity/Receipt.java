package com.receipt.expensetracker.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity @Table(name = "receipts")
@Getter @Builder @AllArgsConstructor @NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Receipt {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long receiptId;
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")
    private User user;
    private String imageUrl;
    private LocalDateTime uploadedAt;
}