import os
import hashlib
import json


def save_test_case(problem, base_dir):
    spj = problem.get('spj', {})
    test_cases = {}
    for index, item in enumerate(problem['test_cases']):
        input_content = item.get('input')
        output_content = item.get('output')
        if input_content:
            with open(
                os.path.join(base_dir, str(index + 1) + '.in'),
                'w',
                encoding='utf-8',
            ) as f:
                f.write(input_content)
        if output_content:
            with open(
                os.path.join(base_dir, str(index + 1) + '.out'),
                'w',
                encoding='utf-8',
            ) as f:
                f.write(output_content)
        if spj:
            one_info = {
                'input_size': len(input_content),
                'input_name': f'{index + 1}.in',
            }
        else:
            one_info = {
                'input_size': len(input_content),
                'input_name': f'{index + 1}.in',
                'output_size': len(output_content),
                'output_name': f'{index + 1}.out',
                'stripped_output_md5': hashlib.md5(
                    output_content.rstrip().encode('utf-8')
                ).hexdigest(),
            }
        test_cases[index] = one_info
    info = {'spj': True if spj else False, 'test_cases': test_cases}
    with open(os.path.join(base_dir, 'info'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(info, indent=4))
    return info

if __name__ == "__main__":
    problem = {'spj': False, 'title': 'A+B Problem', 'test_cases' : [{'input':'1.in', 'output':'1.out'}]}
    save_test_case(problem, './demo/')