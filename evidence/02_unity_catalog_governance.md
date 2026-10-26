# Unity Catalog — govern it
_Captured 2026-10-26 06:57 UTC from workspace `hunter` (catalog `harbourline`) by `scripts/collect_evidence.py`._

## Access is defined once: role scopes (governance.role_scope)

| principal | scope_type | scope_value |
|---|---|---|
| b55e85ff-6c35-4f89-812a-80106438c2b6 | portfolio | * |
| b55e85ff-6c35-4f89-812a-80106438c2b6 | deal_room | * |
| jennifer.wang@databricks.com | portfolio | * |
| jennifer.wang@databricks.com | deal_room | * |
| role-approver | portfolio | * |
| role-business-user | portfolio | Fund I |
| role-external-gp | deal_room | Solace Grid Energy |
| role-it-ai-owner | portfolio | * |

_8 row(s)_

## Row-filter function

```sql
DESCRIBE FUNCTION EXTENDED harbourline.governance.scope_match
```

| function_desc |
|---|
| Function:      harbourline.governance.scope_match |
| Type:          SCALAR |
| Input:         p_type STRING COLLATE UTF8_BINARY |
|                p_val  STRING COLLATE UTF8_BINARY |
| Returns:       BOOLEAN |
| Comment:       Row visible when the active identity (assumed role via current_user()) has that scope in role_scope |
| Collation:     UTF8_BINARY |
| Deterministic: true |
| Data Access:   READS SQL DATA |
| Configs:       runtime.databricks.sql.functions.counter_diff.enabled=true |
|                runtime.databricks.sql.functions.time_bucket.enabled=true |
|                spark.databricks.ai.adaptiveBatch.initialSize=4 |
|                spark.databricks.ai.adaptiveBatch.maxRetries=100 |
|                spark.databricks.ai.adaptiveBatch.partitionJitterEnabled=true |
|                spark.databricks.ai.adaptiveBatch.retriableInvokeStatusCodes=UNAVAILABLE,RESOURCE_EXHAUSTED,DEADLINE_EXCEEDED,ABORTED,CANCELLED |
|                spark.databricks.ai.adaptiveBatch.retryMaxDelayMs=120000 |
|                spark.databricks.ai.grpc.sync.retriableStatusCodes=UNAVAILABLE,RESOURCE_EXHAUSTED,DEADLINE_EXCEEDED,ABORTED,CANCELLED |
|                spark.databricks.docingest.apdfl.sandbox.enabled=false |
|                spark.databricks.docingest.batchEval.size=8 |
|                spark.databricks.docingest.contentElementTypes.excluded= |
|                spark.databricks.docingest.maxDocumentPages=1000 |
|                spark.databricks.docingest.pagination.concurrency=1 |
|                spark.databricks.docingest.pdf.drawFlags=USE_ANNOT_FACES |
|                spark.databricks.docingest.stage2.descriptionModel=databricks-gemma-3-12b |
|                spark.databricks.docingest.version.default=2.0 |
|                spark.databricks.docingest.version.supported=2.0 |
|                spark.databricks.sql.ai.hermes.embeddingBatch.enabled=true |
|                spark.databricks.sql.ai.partitionProcessor.aimdLimiter.enabled=true |
|                spark.databricks.sql.ai.partitionProcessor.aimdLimiter.max=200 |
|                spark.databricks.sql.ai.partitionProcessor.globalMaxInFlightElements=10240 |
|                spark.databricks.sql.ai.partitionProcessor.maxBufferedResults=512 |
|                spark.databricks.sql.ai.partitionProcessor.maxInFlightElements=200 |
|                spark.databricks.sql.ai.partitionProcessor.maxWaitTimeSeconds=172800 |
|                spark.databricks.sql.ai.remoteFunction.grpc.initialRetryInterval=100 |
|                spark.databricks.sql.ai.remoteFunction.grpc.maxRetryInterval=10000 |
|                spark.databricks.sql.ai.remoteFunction.grpc.retryIntervalJitterFactor=1.0 |
|                spark.databricks.sql.ai.remoteFunction.grpc.richArguments.enabled=true |
|                spark.databricks.sql.ai.remoteFunction.hermes.extendedTypeConversion.enabled=true |
|                spark.databricks.sql.expression.aiFunctions.repartition=0 |
|                spark.databricks.sql.functions.aiDetectAnomalies.enabled=false |
|                spark.databricks.sql.functions.aiForecast.enabled=true |
|                spark.databricks.sql.functions.aiForecastV2.enabled=false |
|                spark.databricks.sql.functions.aiForecastV2.modelPath=/Volumes/system/__internal_ai/ai_forecast_volume/forecaster_v5 |
|                spark.databricks.sql.functions.aiFunctions.aclValidateAllFunctions=true |
|                spark.databricks.sql.functions.aiFunctions.adaptiveThreadPool.clusterSizeBasedGlobalParallelism.scaleFactor=512.0 |
|                spark.databricks.sql.functions.aiFunctions.adaptiveThreadPool.debugLogEnabled=true |
|                spark.databricks.sql.functions.aiFunctions.adaptiveThreadPool.dynamicPoolSizeEnabled=false |
|                spark.databricks.sql.functions.aiFunctions.adaptiveThreadPool.enabled=true |
|                spark.databricks.sql.functions.aiFunctions.adaptiveThreadPool.maxPoolSize=2048 |
|                spark.databricks.sql.functions.aiFunctions.adaptiveThreadPool.maxPoolSize.aiParseDocument=64 |
|                spark.databricks.sql.functions.aiFunctions.adaptiveThreadPool.scaleUpThresholdCurrentQpsIncreaseRatio=0.0 |
|                spark.databricks.sql.functions.aiFunctions.adaptiveThreadPool.scaleUpThresholdSuccessRatio=0.95 |
|                spark.databricks.sql.functions.aiFunctions.adaptiveThreadPool.scaleUpThresholdTotalQpsIncreaseRatio=0.0 |
|                spark.databricks.sql.functions.aiFunctions.adaptiveThreadPool.taskWaitTimeInSeconds=1000 |
|                spark.databricks.sql.functions.aiFunctions.adaptiveThreadPool.threadKeepAliveTimeInSeconds=600 |
|                spark.databricks.sql.functions.aiFunctions.adaptiveThreadPool.useDynamicTaskQueueExecutor=false |
|                spark.databricks.sql.functions.aiFunctions.batch.aiQuery.embedding.request.size=40 |
|                spark.databricks.sql.functions.aiFunctions.batch.execution.enabled=true |
|                spark.databricks.sql.functions.aiFunctions.batch.execution.size=2048 |
|                spark.databricks.sql.functions.aiFunctions.batchInferenceApi.enabled=true |
|                spark.databricks.sql.functions.aiFunctions.batchSession.enabled=true |
|                spark.databricks.sql.functions.aiFunctions.batchSession.terminate.enabled=true |
|                spark.databricks.sql.functions.aiFunctions.createBatchSessionOnExecutor=false |
|                spark.databricks.sql.functions.aiFunctions.decimal.dataType.enabled=true |
|                spark.databricks.sql.functions.aiFunctions.disabled=false |
|                spark.databricks.sql.functions.aiFunctions.embeddingsEndpointName=databricks-gte-large-en |
|                spark.databricks.sql.functions.aiFunctions.extract.tileMetadata.enabled=true |
|                spark.databricks.sql.functions.aiFunctions.grpc.enabled=true |
|                spark.databricks.sql.functions.aiFunctions.hermes.aiQuery.directBuilder.enabled=true |
|                spark.databricks.sql.functions.aiFunctions.hermes.aiQuery.failOnError.enabled=true |
|                spark.databricks.sql.functions.aiFunctions.hermes.aiQuery.files.enabled=true |
|                spark.databricks.sql.functions.aiFunctions.hermes.errorTemplate.enabled=true |
|                spark.databricks.sql.functions.aiFunctions.hermes.partitionProcessorConf.enabled=true |
|                spark.databricks.sql.functions.aiFunctions.hermesEnabledFunctions=ai_classify,ai_extract,ai_prep_search,ai_parse_document,ai_search,ai_query,ai_mask,ai_enrich,ai_transcribe,ai_summarize,ai_fix_grammar,ai_analyze_sentiment,ai_translate,ai_decide |
|                spark.databricks.sql.functions.aiFunctions.includeWorkspaceUrl=false |
|                spark.databricks.sql.functions.aiFunctions.model.parameters.enabled=true |
|                spark.databricks.sql.functions.aiFunctions.modelEndpointTypeParsing.enabled=true |
|                spark.databricks.sql.functions.aiFunctions.multiModality.model.list=databricks-llama-4-maverick,databricks-claude-sonnet-4,databricks-claude-3-7-sonnet,databricks-gemma-3-12b,databricks-gpt-5,databricks-gpt-5-mini,databricks-gpt-5-nano,databricks-gpt-5-1,databricks-gpt-5-2,databricks-gemini-2-5-flash,databricks-gemini-2-5-pro,databricks-gemini-3-flash,databricks-gemini-3-pro,databricks-claude-haiku-4-5 |
|                spark.databricks.sql.functions.aiFunctions.multiModality.useCapabilitiesApi=true |
|                spark.databricks.sql.functions.aiFunctions.nullInputJsonOutput={"response":null,"error_message":null} |
|                spark.databricks.sql.functions.aiFunctions.purposeBuiltFunctions.batch.execution.enabled=true |
|                spark.databricks.sql.functions.aiFunctions.purposeBuiltFunctions.translate.instruction=### Instruction  Translate the provided text to %s, and output only the translated text in the target language in this format: <DBSQLAI>translated text</DBSQLAI>.  If the text is already in the target language, output the provided text.  ### Text  %s |
|                spark.databricks.sql.functions.aiFunctions.registry.enabled=true |
|                spark.databricks.sql.functions.aiFunctions.remoteFunction.grpc.batch.maxConcurrentRequests=2048 |
|                spark.databricks.sql.functions.aiFunctions.remoteHttpClient.maxConnections=2048 |
|                spark.databricks.sql.functions.aiFunctions.remoteHttpClient.timeoutInSeconds=360 |
|                spark.databricks.sql.functions.aiFunctions.safe.inference.enabled=true |
|                spark.databricks.sql.functions.aiFunctions.scalingReasonLogging.enabled=true |
|                spark.databricks.sql.functions.aiFunctions.similarity.batch.execution.enabled=false |
|                spark.databricks.sql.functions.aiFunctions.useDedicatedHttpClient=true |
|                spark.databricks.sql.functions.aiFunctions.useGrpcForSessionManagement=true |
|                spark.databricks.sql.functions.aiFunctions.vectorSearch.initialRetryIntervalMillis=1000 |
|                spark.databricks.sql.functions.aiFunctions.vectorSearch.maxRetryInterval=120000 |
|                spark.databricks.sql.functions.aiFunctions.vectorSearch.retryIntervalMultiplierFactor=2.0 |
|                spark.databricks.sql.functions.aiGen.endpointName=databricks-meta-llama-3-3-70b-instruct |
|                spark.databricks.sql.functions.aiQuery.hybrid.reasoning.foundation.model.list=databricks-claude-3-7-sonnet,databricks-gemini-2-5-pro,databricks-gemini-2-5-flash,databricks-gemini-3-flash |
|                spark.databricks.sql.functions.aiQuery.openAI.oSeries.model.list=o1-mini,o1,o3-mini,o3,o4-mini,gpt-5,gpt-5-mini,gpt-5-nano,GPT-5,GPT-5 Mini,GPT-5 Nano |
|                spark.databricks.sql.functions.aiQuery.temperature.whitelistMode.enabled=true |
|                spark.databricks.sql.functions.aiQuery.ucModelService.enabled=true |
|                spark.databricks.sql.functions.vectorSearch.byEmbeddingVector.enabled=false |
|                spark.databricks.sql.functions.vectorSearch.enabled=true |
|                spark.databricks.sql.functions.vectorSearch.use.indexIdentifierOnly=true |
|                spark.databricks.sql.rowColumnAccess.useEffectivePolicies.enabled=true |
|                spark.sql.analyzer.dontDeduplicateExpressionIfExprIdInOutput=false |
|                spark.sql.ansi.enabled=false |
|                spark.sql.ansi.enforceAnsiTypeCoercion=true |
|                spark.sql.ansi.enforceReservedKeywords=false |
|                spark.sql.artifact.includeClusterScopedJars=false |
|                spark.sql.artifact.isolation.enabled=false |
|                spark.sql.avro.datetimeRebaseModeInRead=LEGACY |
|                spark.sql.avro.datetimeRebaseModeInWrite=LEGACY |
|                spark.sql.columnVector.offheap.enabled=true |
|                spark.sql.copyInto.timeout.threadDump.enabled=false |
|                spark.sql.cte.recursion.enabled=true |
|                spark.sql.datetime.java8API.enabled=true |
|                spark.sql.excel.streaming.enabled=true |
|                spark.sql.fileType.enabled=false |
|                spark.sql.functions.remoteHttpClient.redirectLogging.enabled=true |
|                spark.sql.functions.remoteHttpClient.retryOn400TimeoutError=true |
|                spark.sql.functions.remoteHttpClient.retryOnSocketTimeoutException=true |
|                spark.sql.hive.convertCTAS=true |
|                spark.sql.insertIntoReplaceUsing.disallowMisalignedColumns.enabled=true |
|                spark.sql.insertIntoReplaceUsing.oldDPOCodePath.enabled=true |
|                spark.sql.legacy.blockCreateTempTableUsingProvider=true |
|                spark.sql.legacy.codingErrorAction=true |
|                spark.sql.legacy.createHiveTableByDefault=false |
|                spark.sql.legacy.observeMetricsAggregateAllAttempts=true |
|                spark.sql.legacy.useLegacyXMLParser.migrationValidation.enabled=false |
|                spark.sql.orc.compression.codec=snappy |
|                spark.sql.parquet.compression.codec=snappy |
|                spark.sql.parquet.datetimeRebaseModeInRead=LEGACY |
|                spark.sql.parquet.datetimeRebaseModeInWrite=LEGACY |
|                spark.sql.path.enabled=true |
|                spark.sql.photon.skipIndexForTextSearch.indexingBitmapAgg.forceSerializedOutput=false |
|                spark.sql.photon.skipIndexForTextSearch.indexingBitmapAndAgg.enabled=true |
|                spark.sql.pivot.emptyBucketReturnsAggregateDefault=false |
|                spark.sql.scripting.enabled=true |
|                spark.sql.scripting.maxNumberOfCharacters=1000000 |
|                spark.sql.scripting.maxNumberOfLines=30000 |
|                spark.sql.searchIndex.alterColumnSyntax.enabled=true |
|                spark.sql.searchIndex.clusterBy.enabled=true |
|                spark.sql.searchIndex.clusterBy.generalization.enabled=true |
|                spark.sql.secondaryIndex.asyncCreation.enabled=false |
|                spark.sql.secondaryIndex.manualRefresh.disabled=false |
|                spark.sql.secondaryIndex.rowIdWatermark.enabled=true |
|                spark.sql.secondaryIndex.showInDescribeTable=true |
|                spark.sql.secondaryIndex.ucIntegration.enabled=false |
|                spark.sql.session.timeZone=Etc/UTC |
|                spark.sql.shuffleDependency.skipMigration.enabled=true |
|                spark.sql.skipIndexForTextSearch.enabled=true |
|                spark.sql.skipIndexForTextSearch.ngramIndex.parameterCalculation=true |
|                spark.sql.skipIndexForTextSearch.patternBucketCount=524288 |
|                spark.sql.skipIndexForTextSearch.rowsBatchSize=32 |
|                spark.sql.skipIndexForTextSearch.v2.enabled=true |
|                spark.sql.sources.commitProtocolClass=com.databricks.sql.transaction.directory.DirectoryAtomicCommitProtocol |
|                spark.sql.sources.default=delta |
|                spark.sql.sqlgateway.retry.readyOnlyCommands.v2.enabled=true |
|                spark.sql.sqlgateway.retry.stateChangingCommands.enabled=true |
|                spark.sql.sqlgateway.retryFailFastModeEnabled=true |
|                spark.sql.standardIndex.costBasedSelection.enabled=true |
|                spark.sql.standardIndex.enabled=false |
|                spark.sql.streaming.checkpoint.fileChecksum.enabled=false |
|                spark.sql.streaming.optimizer.subqueryEarlyUnnesting.enabled=false |
|                spark.sql.streaming.stopTimeout=15s |
|                spark.sql.thriftServer.interruptOnCancel=true |
|                spark.sql.thriftServer.queryTimeout=0 |
|                spark.sql.thriftserver.scheduler.pool=thriftserver-session-01f1d104-f663-175c-bf46-dbd708da09c3 |
|                spark.sql.timeType.enabled=false |
|                spark.sql.timestampNanosTypes.enabled=false |
|                spark.sql.validateColumnNamesSync.throwException=true |
|                spark.sql.variable.substitute=false |
|                spark.sql.variant.pushVariantIntoScan=true |
|                spark.sql.variant.pushVariantIntoScan.deferCastError=true |
|                spark.sql.variant.writeShredding.enabled=true |
|                spark.sql.vectorIndex.enabled=false |
|                spark.sql.vectorIndex.numCentroidsScalingFactor=4 |
|                spark.sql.vectorIndex.optimization.enabled=false |
|                spark.sql.vectorIndex.optimization.enabledForCommands=false |
|                spark.thriftserver.cloudStoreBasedRowSet.arrowRowLevelByteTrimming=false |
| Owner:         jennifer.wang@databricks.com |
| Create Time:   Mon Oct 26 06:17:47 UTC 2026 |
| Body:          EXISTS (SELECT 1 FROM harbourline.governance.role_scope s                  WHERE s.principal = current_user() AND s.scope_type = p_type AND (s.scope_value = '*' OR s.scope_value = p_val)) |
| SQL Path:      system.builtin, system.ai, neo4j_account_poc1.default |

_183 row(s)_

## Tag-based ABAC policy on the vdr schema + file row filter

| table_name | column_name | tag_name |
|---|---|---|
| alerts | portfolio | hl_portfolio |
| alerts | portfolio | domain_portfolio_management |
| checklist_items | portfolio | hl_portfolio |
| checklist_items | portfolio | domain_portfolio_management |
| checklist_status | portfolio | domain_portfolio_management |
| checklist_status | portfolio | hl_portfolio |
| doc_extracts | portfolio | hl_portfolio |
| doc_extracts | portfolio | domain_portfolio_management |
| doc_parsed | portfolio | domain_portfolio_management |
| doc_parsed | portfolio | hl_portfolio |
| file_content | portfolio | hl_portfolio |
| file_content | portfolio | domain_portfolio_management |
| income_statement | portfolio | hl_portfolio |
| income_statement | portfolio | domain_portfolio_management |
| investments | portfolio | domain_portfolio_management |
| investments | portfolio | hl_portfolio |
| performance_summary | portfolio | domain_portfolio_management |
| performance_summary | portfolio | hl_portfolio |
| portfolio_kpis | portfolio | hl_portfolio |
| portfolio_kpis | portfolio | domain_portfolio_management |
| reporting_calendar | portfolio | hl_portfolio |
| reporting_calendar | portfolio | domain_portfolio_management |
| risks | portfolio | hl_portfolio |
| risks | portfolio | domain_portfolio_management |
| value_bridge | portfolio | domain_portfolio_management |
| value_bridge | portfolio | hl_portfolio |

_26 row(s)_

## The same query, run as each role (row filters applied by Unity Catalog, no app code)

```sql
SELECT current_user() AS identity,
  (SELECT count(*) FROM harbourline.vdr.investments) AS companies_visible,
  (SELECT count(DISTINCT portfolio) FROM harbourline.vdr.investments) AS portfolios_visible,
  (SELECT count(*) FROM harbourline.vdr.file_register WHERE deal_room = 'Solace Grid Energy') AS solace_grid_files_visible,
  (SELECT round(max(value) / 1e9, 2) FROM harbourline.vdr.portfolio_kpis WHERE kpi = 'total_invested_usd' AND period = '2026-Q2') AS total_invested_usd_bn
```

## as role-business-user

| identity | companies_visible | portfolios_visible | solace_grid_files_visible | total_invested_usd_bn |
|---|---|---|---|---|
| role-business-user | 6 | 1 | 6 | 2.86 |

_1 row(s)_

## as role-approver

| identity | companies_visible | portfolios_visible | solace_grid_files_visible | total_invested_usd_bn |
|---|---|---|---|---|
| role-approver | 7 | 2 | 6 | 2.86 |

_1 row(s)_

## as role-external-gp

| identity | companies_visible | portfolios_visible | solace_grid_files_visible | total_invested_usd_bn |
|---|---|---|---|---|
| role-external-gp | 0 | 0 | 0 | NULL |

_1 row(s)_
