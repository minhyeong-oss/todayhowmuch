package com.receipt.expensetracker.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity @Table(name = "spending_analyses")
@Getter @Builder @AllArgsConstructor @NoArgsConstructor(access = AccessLevel.PROTECTED)
public class SpendingAnalysis {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long analysisId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")
    private User user;

    private String analysisContent; // 분석 결과 리포트

    // yearMonth 대신 targetMonth로 변경 (MySQL 예약어 충돌 회피)
    private String targetMonth;
}