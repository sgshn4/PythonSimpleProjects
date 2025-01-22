import reforming_increment
import utils
paths_in = ['input\\input1.cs',
            'input\\input2.cs',
            'input\\input3.cs',
            'input\\input4.cs',
            'input\\input5.cs']
paths_out = ['output\\output1.cs',
             'output\\output2.cs',
             'output\\output3.cs',
             'output\\output4.cs',
             'output\\output5.cs']

for i in range(len(paths_in)):
    utils.write_file(paths_out[i], reforming_increment.solution(utils.read_file(paths_in[i])))