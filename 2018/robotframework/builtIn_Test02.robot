*** Setting ***
Documentation     Title: a basic library for RF
Library           Collections
Library           DateTime
Library           Dialogs
Library           OperatingSystem
Library           Screenshot
Library           String

*** Variables ***
${PATH}           ${CURDIR}/Testsuite04_example.txt

*** Test Cases ***
Test__Collections__01
    [Documentation]    list operation
    ...    fail ======todo
    Append To List    ${L1}    xxx
    Append To List    ${L1}    x    y    z

Test__Dialogs__02
    ${username} =    Get Selection From User    Select user name    user1    user2    admin
    ${username} =    Get Value From User    Input user name    default
    ${password} =    Get Value From User    Input password    hidden=yes

Test__OperatingSystem__03
    [Documentation]    123
    ...
    ...    TEMPDIR = c:\users\ywx536~1\appdata\local\temp
    ...    C:\Users\ywx536122\AppData\Local\Temp\RIDEpmppz1.d
    ...    ${output} = Run ${TEMPDIR}${/}script.py arg
    ...    ~/file.txt 是 C:\Users\ywx536122\file.txt
    ...
    ...    Description
    Create File    ${PATH}    ${TEMPDIR}
    File Should Exist    ${PATH}
    Copy File    ${PATH}    ./Testsuite04_example_copy.txt
    ${output} =    Run    Testsuite04_script.py hahaha
    Should Be Equal    ${output}    22-->hahaha

Test__OperatingSystem__04
    ${output} =    Run    dir
    Log    ${output}
    ${result} =    Run    ${CURDIR}${/}Testsuite04_script.py hahaha04
    Should Contain    ${result}    haha
    Should Not Contain    ${result}    FAIL
    File Should Be Empty    ./0.txt

Test__Screenshot__05
    Set Screenshot Directory    ${CURDIR}
    Take Screenshot    Testsuite04_screenshot_1.jpg

Test__String__06
    ${str1} =    Convert To Lowercase    ABC
    ${str2} =    Convert To Lowercase    1A2c3D
    Should Be Equal    ${str1}    abc
    Should Be Equal    ${str2}    1a2c3d
    ${str1} =    Convert To Uppercase    abc
    ${str2} =    Convert To Uppercase    1a2C3d
    Should Be Equal    ${str1}    ABC
    Should Be Equal    ${str2}    1A2C3D

Test__Log__07
    @{list} =    Create List    first    second    third
    Length Should Be    ${list}    3
    Log Many    @{list}
    &{dict} =    Create Dictionary    first=1    second=${2}    ${3}=third
    Length Should Be    ${dict}    3
    Log    ${dict.first}

*** Keywords ***
Find Index
    [Arguments]    ${element}    @{items}
    ${index} =    Set Variable    ${0}
    : FOR    ${item}    IN    @{items}
    \    Return From Keyword If    '${item}' == '${element}'    ${index}
    \    ${index} =    Set Variable    ${index + 1}
    Return From Keyword    ${-1}    # Also [Return] would work here.
