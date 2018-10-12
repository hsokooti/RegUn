

def job_script(setting, job_name=None, phase=None, cn=None, out=None, outfinal=None, script_address=None, job_output=None):
    text = """#!/bin/bash
#$ -S /bin/bash 
#$ -j Y 
#$ -V 
"""
    text = text + '#$ -o ' + job_output + '\n'
    text = text + '#$ -q ' + setting['cluster_queue'] + '\n'
    text = text + '#$ -N ' + job_name + '\n'
    text = text + '#$ -l h_vmem=' + setting['cluster_memory'] + '\n'

    text = text + 'python ' + script_address + ' --phase ' + str(phase) + ' --cn ' + str(cn)
    if out is not None:
        text = text + ' --out ' + str(out)
    if outfinal is not None:
        text = text + ' --outfinal ' + str(outfinal)
    text = text + '\n'
    return text
