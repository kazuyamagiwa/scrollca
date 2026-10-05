' Infinite scrolling Sierpiński triangle via Rule 90 cellular automaton.
' FreeBASIC (fbc) / QB64-friendly dialect.
'
' Build & run with FreeBASIC:
'   fbc rule90_scroll.bas
'   ./rule90_scroll
'
' Press Ctrl+C to stop.

Const ALIVE As String = "#"
Const DEAD As String = " "
Const DEFAULT_WIDTH As Integer = 79
Const DELAY_MS As Integer = 50

Declare Function MakeInitialRow(ByVal W As Integer) As String
Declare Function NextGeneration(ByRef Cur As String, ByVal W As Integer) As String

Dim As Integer WidthCells
Dim As String Row

WidthCells = DEFAULT_WIDTH
Row = MakeInitialRow(WidthCells)

Do
    Print Row
    Row = NextGeneration(Row, WidthCells)
    Sleep DELAY_MS, 1
Loop

Function MakeInitialRow(ByVal W As Integer) As String
    Dim As String R = String(W, DEAD)
    Mid(R, (W \ 2) + 1, 1) = ALIVE
    Return R
End Function

' Rule 90 with toroidal edges: a cell is alive iff its left and right neighbors differ.
Function NextGeneration(ByRef Cur As String, ByVal W As Integer) As String
    Dim As String Nxt = String(W, DEAD)
    Dim As Integer I, L, R
    Dim As String LeftCell, RightCell

    For I = 1 To W
        L = I - 1
        If L < 1 Then L = W
        R = I + 1
        If R > W Then R = 1

        LeftCell = Mid(Cur, L, 1)
        RightCell = Mid(Cur, R, 1)

        If LeftCell <> RightCell Then
            Mid(Nxt, I, 1) = ALIVE
        End If
    Next I

    Return Nxt
End Function
