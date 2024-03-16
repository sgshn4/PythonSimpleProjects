import utils
import solution

paths_in = ['input/input1.txt',
            'input/input2.txt',
            'input/input3.txt',
            'input/input4.txt',
            'input/input5.txt']
paths_out = ['output/output1.txt',
             'output/output2.txt',
             'output/output3.txt',
             'output/output4.txt',
             'output/output5.txt']
for i in range(len(paths_in)):
    utils.write_file(paths_out[i], solution.solution(utils.read_file(paths_in[i])))
