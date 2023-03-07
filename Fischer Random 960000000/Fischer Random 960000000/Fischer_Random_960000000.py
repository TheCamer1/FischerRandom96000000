import random
from itertools import count
import chess
import chess.engine

stockfish = chess.engine.SimpleEngine.popen_uci("C:/Code/FischerRandom960000000/stockfish/stockfish.exe")

darkSquares = [
    22, 24, 26, 28,
    31, 33, 35, 37,
    42, 44, 46, 48,
    51, 53, 55, 57,
    62, 64, 66, 68,
    71, 73, 75, 77,
    82, 84, 86, 88,
    91, 93, 95, 97
]
lightSquares = [x - 1 for x in darkSquares]

board = None
whitePieces = "PPPPPPPPRNBQKBNR"
blackPieces = "pppppppprnbqkbnr"

N, E, S, W = -10, 1, 10, -1
whiteDirections = {
    'P': (N+W, N+E),
    'N': (N+N+E, E+N+E, E+S+E, S+S+E, S+S+W, W+S+W, W+N+W, N+N+W),
    'B': (N+E, S+E, S+W, N+W),
    'R': (N, E, S, W),
    'Q': (N, E, S, W, N+E, S+E, S+W, N+W),
    'K': (N, E, S, W, N+E, S+E, S+W, N+W)
}
blackDirections = {
    'p': (S+W, S+E),
    'n': whiteDirections['N'],
    'b': whiteDirections['B'],
    'r': whiteDirections['R'],
    'q': whiteDirections['Q'],
    'k': whiteDirections['K'],
}

def getRandomPosition(start, end, exclusions):
    return random.choice(list(set([x for x in range(start, end)]) - set(exclusions)));

def getFen(board, printBoard=True):
    rows = []
    for i in range(2,10):
        row = ""
        for j in range(1,9):
            character = board[10*i + j]
            if character.isspace():
                continue
            row += ' ' + character
        if printBoard:
            print(row)
        rows.append(row)
    fen = ""
    for row in rows:
        blankSpaces = 0
        for character in row:
            if character.isspace():
                continue
            if character != ".":
                if blankSpaces != 0:
                    fen += str(blankSpaces)
                    blankSpaces = 0
                fen += character
                continue
            blankSpaces += 1
        if blankSpaces != 0:
            fen += str(blankSpaces)
        fen += '/'
    fen = fen[:-1]
    fen += " w - - 0 1"
    return fen

def getExclusions():
    return [x for x in range(20)] + \
        [x for x in range(100,120)] + \
        [x for x in range(20,91,10)] + \
        [x for x in range(29,100,10)]

def getBoard():
    return list(
    '         \n'  #   0 -  9
    '         \n'  #  10 - 19
    ' ........\n'  #  20 - 29
    ' ........\n'  #  30 - 39
    ' ........\n'  #  40 - 49
    ' ........\n'  #  50 - 59
    ' ........\n'  #  60 - 69
    ' ........\n'  #  70 - 79
    ' ........\n'  #  80 - 89
    ' ........\n'  #  90 - 99
    '         \n'  # 100 -109
    '         \n'  # 110 -119
)

def setPieces(board, pieces, exclusions):
    bishopExclusions = None
    for piece in pieces:
        if piece == 'K' or piece == 'k':
            continue
        position = 0
        if piece == 'p' or piece == 'P':
            position = getRandomPosition(31, 89, exclusions)
        else:
            position = getRandomPosition(21, 99, exclusions)

        if piece == 'b' or piece == 'B':
            if bishopExclusions == None:
                if position in darkSquares:
                    bishopExclusions = darkSquares
                if position in lightSquares:
                    bishopExclusions = lightSquares
            else:
                position = getRandomPosition(21, 99, bishopExclusions + exclusions)
        board[position] = piece
        exclusions.append(position)

def setKing(board, king, enemyDirections, exclusions):
    attackedSquares = []
    for piece in enemyDirections.keys():
        for position in [i for i, x in enumerate(board) if x == piece]:
            for direction in enemyDirections[piece]:
                for newPosition in count(position+direction, direction):
                    square = board[newPosition]
                    if square != '.':
                        break
                    attackedSquares.append(newPosition)
                    if piece in 'PNKpnk':
                        break
    kingPosition = getRandomPosition(21, 99, exclusions + attackedSquares)
    board[kingPosition] = king
    exclusions.append(kingPosition)

def getEvaluation(fen,timeToThink):
    engineBoard = chess.Board(fen)
    info = stockfish.analyse(engineBoard, chess.engine.Limit(time=timeToThink))
    score = info["score"].white()
    if "#" in str(score):
        return score
    else:
        return float(str(score))/100

def oneByOne():
    while True:
        exclusions = getExclusions()
        board = getBoard()
        setPieces(board, whitePieces, exclusions)
        setPieces(board, blackPieces, exclusions)
        setKing(board, 'K', blackDirections, exclusions)
        setKing(board, 'k', whiteDirections, exclusions)
        fen = getFen(board)
        print(fen)
        evaluation = getEvaluation(fen,1)
        print(evaluation)
        input()
            
def findEqualPositions():
    while True:
        exclusions = getExclusions()
        board = getBoard()
        setPieces(board, whitePieces, exclusions)
        setPieces(board, blackPieces, exclusions)
        setKing(board, 'K', blackDirections, exclusions)
        setKing(board, 'k', whiteDirections, exclusions)
        fen = getFen(board, False)
        evaluation = getEvaluation(fen,2)
        if '#' not in str(evaluation) and evaluation < 3 and evaluation > -3 and str(evaluation) != "0.0":
            evaluation = getEvaluation(fen,5)
            if '#' not in str(evaluation) and evaluation < 2 and evaluation > -2 and str(evaluation) != "0.0":
                evaluation = getEvaluation(fen,30)
                if '#' not in str(evaluation) and evaluation < 2 and evaluation > -2 and str(evaluation) != "0.0":
                    evaluation = getEvaluation(fen,120)
                    if '#' not in str(evaluation) and evaluation < 1.5 and evaluation > -1.5 and str(evaluation) != "0.0":
                        print("Found!", evaluation)
                        print(fen)
oneByOne()