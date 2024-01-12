CREATE OR REPLACE TABLE audit.cvetkov_d_container_date_next_before
ENGINE = Memory() AS
(

WITH
SVOD AS ( 
	SELECT --TOP(10000)
		toInt32(source_row) AS source_row,
		container_number_raw,
		date_raw,
		container_number,
		toDateTime(`date`,'Europe/Moscow') AS `date`
	FROM 
		audit.cvetkov_d_container_date_next_before
--		audit.container_data_next_before
--) SELECT * FROM SVOD			
),
CITTRANS AS ( 
		SELECT 
			CITTRANS_OPER.mOprId,
			CITTRANS_OPER.KontOtprId,
			EsrOper,
			Nom_Vag,
			container_operation_code,
			shipment_document_number,
			Date_pop,
			container_number,
			`date`
		FROM 
			cittrans__container_oper_v3 AS CITTRANS_OPER
			LEFT JOIN SVOD ON SVOD.container_number = CITTRANS_OPER.container_number
		WHERE  
			CITTRANS_OPER.container_number IN (SELECT DISTINCT container_number FROM SVOD)
) SELECT * FROM CITTRANS 

--
--SELECT max(Date_pop) FROM cittrans__container_oper_v3  --WHERE container_number = 'TKRU4396050' 
 ),
	CITTRANS AS (
		SELECT 
			container_number,
			`date`,
			-----------------------------------------------------------------------------------------------------
			argMaxIf(mOprId                  , Date_pop, `date` >= Date_pop) AS mOprId_before,
			argMaxIf(KontOtprId              , Date_pop, `date` >= Date_pop) AS KontOtprId_before,
			argMaxIf(EsrOper                 , Date_pop, `date` >= Date_pop) AS EsrOper_before,			
			argMaxIf(Nom_Vag                 , Date_pop, `date` >= Date_pop) AS Nom_Vag_before,			
			argMaxIf(container_operation_code, Date_pop, `date` >= Date_pop) AS container_operation_code_before,					
			argMaxIf(shipment_document_number, Date_pop, `date` >= Date_pop) AS shipment_document_number_before,	
			argMaxIf(Date_pop                , Date_pop, `date` >= Date_pop) AS Date_pop_before,
			-----------------------------------------------------------------------------------------------------
			argMinIf(mOprId                  , Date_pop, `date` <= Date_pop) AS mOprId_after,
			argMinIf(KontOtprId              , Date_pop, `date` <= Date_pop) AS KontOtprId_after,
			argMinIf(EsrOper                 , Date_pop, `date` <= Date_pop) AS EsrOper_after,			
			argMinIf(Nom_Vag                 , Date_pop, `date` <= Date_pop) AS Nom_Vag_after,			
			argMinIf(container_operation_code, Date_pop, `date` <= Date_pop) AS container_operation_code_after,							
			argMinIf(shipment_document_number, Date_pop, `date` <= Date_pop) AS shipment_document_number_after,	
			argMinIf(Date_pop                , Date_pop, `date` <= Date_pop) AS Date_pop_after
		FROM 
			CITTRANS
		--WHERE 
		--	container_number = 'TKRU4396050'
		GROUP BY
			container_number,
			`date`
--		) SELECT * FROM CITTRANS 
),
CITTRANS AS ( 
		SELECT * /* 
			CITTRANS_OPER.*,
			CITTRANS_OTPR_BEFORE.FirstOperId AS FirstOperId_before,
			CITTRANS_OTPR_AFTER.FirstOperId AS FirstOperId_after	*/		
		FROM 
			CITTRANS AS CITTRANS_OPER
			----------------------------------------------------------------------------------------------
			LEFT JOIN (
				SELECT DISTINCT 
					mOprId,KontOtprId,FirstOperId 
				FROM 
					cittrans__container_otpr_v3 
				WHERE 
					FirstOperId BETWEEN 13000000 AND 40000000 /*AND 
					shipment_document_number IN  (SELECT DISTINCT container_operation_code_before FROM CITTRANS)*/
				) AS CITTRANS_OTPR_BEFORE 
				ON CITTRANS_OPER.mOprId_before = CITTRANS_OTPR_BEFORE.mOprId AND CITTRANS_OPER.KontOtprId_before = CITTRANS_OTPR_BEFORE.KontOtprId
			----------------------------------------------------------------------------------------------	
			LEFT JOIN (
				SELECT DISTINCT 
					mOprId,KontOtprId,FirstOperId 
				FROM 
					cittrans__container_otpr_v3 
				WHERE 
					FirstOperId BETWEEN 13000000 AND 40000000 /*AND 
					shipment_document_number IN  (SELECT DISTINCT container_operation_code_after FROM CITTRANS)*/
				) AS CITTRANS_OTPR_AFTER
				ON CITTRANS_OPER.mOprId_after = CITTRANS_OTPR_AFTER.mOprId AND CITTRANS_OPER.KontOtprId_after = CITTRANS_OTPR_AFTER.KontOtprId				
 --) SELECT * FROM CITTRANS
 ),
 OBRABOTKA AS (
	SELECT 
	*
	FROM 
		SVOD
		LEFT JOIN CITTRANS ON `CITTRANS_OPER.container_number` = `container_number` AND `CITTRANS_OPER.date` = `date`
)
SELECT 
	source_row,
	container_number_raw,
	date_raw,
	container_number,
	`date`,
	--`CITTRANS_OPER.container_number`,`CITTRANS_OPER.date`,`CITTRANS_OPER.mOprId_before`,`CITTRANS_OPER.KontOtprId_before`,
	`CITTRANS_OPER.EsrOper_before`                              AS `EsrOper_before`,
	`CITTRANS_OPER.Nom_Vag_before`                              AS `Nom_Vag_before`,
	`CITTRANS_OPER.container_operation_code_before`             AS `container_operation_code_before`,
	`CITTRANS_OPER.shipment_document_number_before`             AS `shipment_document_number_before`,
	toTimezone(`CITTRANS_OPER.Date_pop_before`,'Europe/Moscow') AS `Date_pop_before`,
	`CITTRANS_OTPR_BEFORE.FirstOperId`                          AS `FirstOperId_before`,	
	--`CITTRANS_OPER.mOprId_after`,`CITTRANS_OPER.KontOtprId_after`,
	`CITTRANS_OPER.EsrOper_after`                               AS `EsrOper_after`,
	`CITTRANS_OPER.Nom_Vag_after`                               AS `Nom_Vag_after`,
	`CITTRANS_OPER.container_operation_code_after`              AS `container_operation_code_after`,
	`CITTRANS_OPER.shipment_document_number_after`              AS `shipment_document_number_after`,
	toTimeZone(`CITTRANS_OPER.Date_pop_after`,'Europe/Moscow')  AS `Date_pop_after`,
	`CITTRANS_OTPR_AFTER.FirstOperId`                           AS `FirstOperId_after`	
	--`CITTRANS_OTPR_BEFORE.mOprId`,`CITTRANS_OTPR_BEFORE.KontOtprId`,
	--`CITTRANS_OTPR_AFTER.mOprId`,`CITTRANS_OTPR_AFTER.KontOtprId`,
FROM 
	OBRABOTKA
)		
		
SELECT
	*
FROM 
	audit.cvetkov_d_res_container_date_next_before	
WHERE 
	container_number = 'TKRU4598560'
