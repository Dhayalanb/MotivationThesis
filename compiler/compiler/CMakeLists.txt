
add_executable(AngoraClang angora_clang.c)
set_target_properties(AngoraClang PROPERTIES OUTPUT_NAME "angora-clang")

add_custom_command(TARGET AngoraClang POST_BUILD
    COMMAND ln -sf "angora-clang" "angora-clang++")
install (TARGETS AngoraClang DESTINATION ${ANGORA_BIN_DIR})
install (FILES ${CMAKE_CURRENT_BINARY_DIR}/angora-clang++ DESTINATION ${ANGORA_BIN_DIR})


add_executable(StaticAnalysis static_analysis_clang.c)
set_target_properties(StaticAnalysis PROPERTIES OUTPUT_NAME "static-analysis-clang")

add_custom_command(TARGET StaticAnalysis POST_BUILD
    COMMAND ln -sf "static-analysis-clang" "static-analysis-clang++")
install (TARGETS StaticAnalysis DESTINATION ${ANGORA_BIN_DIR})
install (FILES ${CMAKE_CURRENT_BINARY_DIR}/static-analysis-clang++ DESTINATION ${ANGORA_BIN_DIR})
