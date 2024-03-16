import utils
import choicer

TABLETS_PATH = 'input/tablets.txt'
INPUT_PATH = 'input/input.txt'
OUTPUT_PATH = 'output/output.txt'
tablets = utils.read_tablets(TABLETS_PATH)
tests = utils.read_data(INPUT_PATH)
result = []
for i in tests:
    result.append(choicer.solution(tablets, int(i[0]), int(i[1]), int(i[2])))
utils.write_file(OUTPUT_PATH, result)

