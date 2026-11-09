cmake_minimum_required(VERSION 3.22)

# ---------------------------------------------------------------------------
# Identidade do plugin (preenchida por novo-plugin.sh).
# São variáveis de cache: depois do primeiro configure, mudar aqui só vale
# apagando build/ (ou passando -DPLUGIN_NAME=... na linha de comando).
# ---------------------------------------------------------------------------
set(PLUGIN_NAME       "__PLUGIN__"    CACHE STRING "Nome do alvo/bundle (letras e números, sem espaço)")
set(PLUGIN_DISPLAY_NAME "__PLUGIN_DISPLAY__" CACHE STRING "Nome exibido no host (pode ter espaço)")
set(PLUGIN_ID         "__PLUGIN_ID__" CACHE STRING "Identificador em minúsculas (pasta, bundle id)")
set(PLUGIN_CODE       "__CODE__"      CACHE STRING "Código do plugin: 4 caracteres, 1 maiúscula")
set(COMPANY_NAME      "__COMPANY__"   CACHE STRING "Nome da empresa exibido no host")
set(MANUFACTURER_CODE "__MFR__"       CACHE STRING "Código do fabricante: 4 caracteres, 1ª maiúscula")
set(BUNDLE_PREFIX     "__BUNDLE__"    CACHE STRING "Prefixo do bundle id (ex.: com.minhaempresa)")
set(PLUGIN_VERSION    "0.1.0"         CACHE STRING "Versão (x.y.z)")

project(${PLUGIN_NAME} VERSION ${PLUGIN_VERSION})

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_OSX_DEPLOYMENT_TARGET "11.0" CACHE STRING "")
if(APPLE)
  set(CMAKE_OSX_ARCHITECTURES "arm64" CACHE STRING "")
endif()

# JUCE: baixado uma vez pelo CMake. Para usar um clone local (mais rápido):
#   cmake -B build -DFETCHCONTENT_SOURCE_DIR_JUCE=/caminho/do/JUCE
include(FetchContent)
FetchContent_Declare(juce
  GIT_REPOSITORY https://github.com/juce-framework/JUCE.git
  GIT_TAG 8.0.16-security
  GIT_SHALLOW TRUE)
FetchContent_MakeAvailable(juce)

# Interface: um único ui/index.html + a biblioteca JS do próprio JUCE (lida da fonte do JUCE).
set(JUCE_JS_DIR "${juce_SOURCE_DIR}/modules/juce_gui_extra/native/javascript")
foreach(f index.js check_native_interop.js)
  if(NOT EXISTS "${JUCE_JS_DIR}/${f}")
    message(FATAL_ERROR "Não achei ${JUCE_JS_DIR}/${f}: a versão do JUCE mudou o caminho da biblioteca JS")
  endif()
endforeach()

juce_add_binary_data(${PLUGIN_NAME}UI SOURCES
  ui/index.html
  "${JUCE_JS_DIR}/index.js"
  "${JUCE_JS_DIR}/check_native_interop.js")

juce_add_plugin(${PLUGIN_NAME}
  COMPANY_NAME "${COMPANY_NAME}"
  BUNDLE_ID "${BUNDLE_PREFIX}.${PLUGIN_ID}"
  PRODUCT_NAME "${PLUGIN_NAME}"
  PLUGIN_NAME "${PLUGIN_DISPLAY_NAME}"
  VERSION "${PLUGIN_VERSION}"
  PLUGIN_MANUFACTURER_CODE ${MANUFACTURER_CODE}
  PLUGIN_CODE ${PLUGIN_CODE}
  FORMATS VST3 AU Standalone
  AU_MAIN_TYPE kAudioUnitType_Effect
  VST3_CATEGORIES Fx
  IS_SYNTH FALSE
  NEEDS_MIDI_INPUT FALSE
  NEEDS_MIDI_OUTPUT FALSE
  NEEDS_WEB_BROWSER TRUE
  COPY_PLUGIN_AFTER_BUILD FALSE)

set(PLUGIN_SOURCES Source/PluginProcessor.cpp Source/PluginEditor.cpp)
set(PLUGIN_DEFINES JUCE_WEB_BROWSER=1 JUCE_USE_CURL=0 JUCE_VST3_CAN_REPLACE_VST2=0)

target_sources(${PLUGIN_NAME} PRIVATE ${PLUGIN_SOURCES})
target_compile_definitions(${PLUGIN_NAME} PUBLIC ${PLUGIN_DEFINES})
target_link_libraries(${PLUGIN_NAME}
  PRIVATE ${PLUGIN_NAME}UI juce::juce_audio_utils juce::juce_gui_extra
  PUBLIC  juce::juce_recommended_config_flags juce::juce_recommended_lto_flags juce::juce_recommended_warning_flags)

# macOS arm64 só carrega binário assinado: assinatura ad-hoc e cópia para ~/Library/Audio/Plug-Ins
if(APPLE)
  set(PLUGIN_DIR "$ENV{HOME}/Library/Audio/Plug-Ins")
  foreach(fmt VST3 AU)
    if(fmt STREQUAL "VST3")
      set(dest "${PLUGIN_DIR}/VST3")
    else()
      set(dest "${PLUGIN_DIR}/Components")
    endif()
    add_custom_command(TARGET ${PLUGIN_NAME}_${fmt} POST_BUILD
      COMMAND codesign --force --sign - --deep "$<TARGET_BUNDLE_DIR:${PLUGIN_NAME}_${fmt}>"
      COMMAND ${CMAKE_COMMAND} -E make_directory "${dest}"
      COMMAND ${CMAKE_COMMAND} -E rm -rf "${dest}/$<TARGET_BUNDLE_DIR_NAME:${PLUGIN_NAME}_${fmt}>"
      COMMAND ${CMAKE_COMMAND} -E copy_directory "$<TARGET_BUNDLE_DIR:${PLUGIN_NAME}_${fmt}>" "${dest}/$<TARGET_BUNDLE_DIR_NAME:${PLUGIN_NAME}_${fmt}>"
      COMMENT "Assinando e instalando ${PLUGIN_NAME} (${fmt}) em ${dest}")
  endforeach()
endif()

# ---------------------------------------------------------------------------
# Testes (sem framework: cada executável devolve 0 se tudo passou)
# ---------------------------------------------------------------------------
enable_testing()

# 1) só o motor de DSP (header sem JUCE)
add_executable(${PLUGIN_NAME}Tests Tests/EngineTests.cpp)
target_include_directories(${PLUGIN_NAME}Tests PRIVATE Source)
add_test(NAME engine COMMAND ${PLUGIN_NAME}Tests)

# 2) o processador real (parâmetros x UI, estado, barramentos, bypass)
juce_add_console_app(${PLUGIN_NAME}ProcTests PRODUCT_NAME "${PLUGIN_NAME}ProcTests" NEEDS_WEB_BROWSER TRUE)
target_sources(${PLUGIN_NAME}ProcTests PRIVATE Tests/ProcessorTests.cpp ${PLUGIN_SOURCES})
target_include_directories(${PLUGIN_NAME}ProcTests PRIVATE Source)
target_compile_definitions(${PLUGIN_NAME}ProcTests PUBLIC ${PLUGIN_DEFINES} JUCE_MODAL_LOOPS_PERMITTED=1
  PLUGIN_UI_HTML="${CMAKE_CURRENT_SOURCE_DIR}/ui/index.html")
target_link_libraries(${PLUGIN_NAME}ProcTests
  PRIVATE ${PLUGIN_NAME}UI juce::juce_audio_utils juce::juce_gui_extra
  PUBLIC  juce::juce_recommended_config_flags juce::juce_recommended_warning_flags)
add_test(NAME processor COMMAND ${PLUGIN_NAME}ProcTests)
