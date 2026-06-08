import numpy as np
import timml
import tim_editor as te
import pickle
import dill
import time
import os
import ark_model

"""
tim_editor_test_large is used to apply the tim_editor system to an actual timflow model and verify whether the results
are exact matches to what would be expected of a 'regular' timflow model with the same inputs

This imports the contents of tim_editor to provide the tim_editor functions
This imports the contents of ark_model to provide the model used in this test
"""
def wrapped_model(resARK):
    """
    wrapped_model turns the model from ark_model into the form required for tim_editor which takes a tuple of resistances as input,
    and as output the printmat=true results of solve
    """
    timml_model= ark_model.model(*resARK)
    mat, rhs = timml_model.solve(printmat=True, silent=True)
    return mat, rhs, timml_model

def test_large():
    """
    Test large injects different resistances into the ARK model, and verifies whether the results are identical to when the model is solved as usual
    """
    print("Running tim_editor test_large, this will not print anything for about a minute")
    timestart=time.time()
    resARK=(7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7)#arbitrary values used during generation of the editlocs
    mat_base, rhs_base, timml_model_base, editlocs= te.load_inputs(resARK,ark_model.model)#load the inputs

    #build the tuple of resistances to be injected
    resARK_test=(83.181, 30.905, 26.115, 188.31, 7.6143, 20.852, 113.49, 31.098, 200, 13.183, 85.785, 188.12, 143.33, 122.5, 200, 9.0117, 86.43) 
    #use the tim_editor surrogate model to get the results
    surrogateresults=ark_model.observaties(te.surrogate_model(editlocs, mat_base, timml_model_base, resARK_test, rhs_base))
    timesurrogate=time.time()

    #run the model regularly by first getting the matrix and then solving it
    mat_def, rhs_def, timml_model_def= wrapped_model(resARK_test)
    te.solve_from(mat_def, rhs_def, timml_model_def)
    actualresults=ark_model.observaties(timml_model_def)
    timeregular=time.time()

    #compare time and check whether results are identical
    print("The tim_editor model took "+str(timesurrogate-timestart)+" seconds to run and the regular tim model took " +str(timeregular-timesurrogate)+" to run")
    print("Passed checks print true:")
    print(~np.any(np.argwhere(mat_base-mat_def)))
    print(np.array_equal(actualresults, surrogateresults))

if __name__ == "__main__":
    #check if editlocs and model were previously generated, and if not generate it now
    if not (os.path.exists("editlocs") and os.path.exists("model")):
        print("Editlocs or model pickles were not found, the tim_editor will now be 'trained', this can take up to 15 minutes")
        resARK=(7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7)
        te.generate_inputs(resARK, wrapped_model)
    test_large()
    
