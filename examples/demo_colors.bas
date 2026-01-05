10 REM ==========================================
20 REM SIMPLE COLOR DEMO
30 REM ==========================================
40 PRINT CHR$(147)
50 PRINT "COMMODORE 64 BASIC - COLOR DEMO"
60 PRINT "================================"
70 PRINT
80 PRINT "Creating colored alphabet pattern..."
90 FOR ROW = 0 TO 24
100 FOR COL = 0 TO 39
110 CHAR = 64 + ((ROW + COL) MOD 26)
120 COLOR = (ROW + COL) MOD 8 + 2
130 POKE 1024 + ROW * 40 + COL, CHAR
140 POKE 55296 + ROW * 40 + COL, COLOR
150 NEXT COL
160 NEXT ROW
170 PRINT "Done! Displaying screen:"
180 PRINT
190 SCREEN
200 PRINT
210 PRINT "Colors: red, cyan, purple, green, blue, yellow, orange, brown"
220 PRINT "Each letter A-Z cycles through colors diagonally"
230 PRINT
240 END
