10 REM Simple color test - shows colored letters at top-left
20 PRINT "Creating colored pattern at top-left..."
30 FOR C = 0 TO 10
40 POKE 1024 + C, 65 + C
50 POKE 55296 + C, C + 2
60 NEXT C
70 PRINT "Displaying SCREEN..."
80 SCREEN
90 END
