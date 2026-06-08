import tim_editor as te
import timml
import seaborn
import numpy as np
import matplotlib.pyplot as plt
"""
tim_editor_test_small is a proof of concept of the tim_editor system used in its development
"""

def build_model(res1, res2):
    """
    This builds the model with two rivers and one polygon used in this example
    """
    timml_model = timml.ModelMaq(
        kaq=[25.0, 40.0],
        z=[0.0, -6.0, -60.0, -60.5, -180.0],
        c=[600.0, 1.0],
        topboundary='semi',
        npor=[None, None, None, None],
        hstar=-2.0,
    )
    timml_kanaal_7 = timml.HeadLineSinkString(
        model=timml_model,
        xy=[(129300, 472699.97884829855),
        (129710.78358869767, 475078.61211107776)],
        hls=-0.4,
        res=res1,
        wh=100.0,
        order=4,
        layers=0,
        label='editableRiver0',
    )
    timml_kanaal_15 = timml.HeadLineSinkString(
        model=timml_model,
        xy=[(129710.78358869767, 475078.61211107776),
        (129807.5714898645, 475639.83041079855)],
        hls=-0.4,
        res=res2,
        wh=100,
        order=4,
        layers=0,
        label='editableRiver1',
    )
    timml_Zones_9 = timml.PolygonInhomMaq(
        model=timml_model,
        xy=[(130678.4530965097, 475010.6402800113),
        (126654.64766173938, 475070.9038971267),
        (128137.3168511925, 478561.1714752517),
        (131635.01547326992, 476434.28662669455),
        (130678.4530965097, 475010.6402800113)],
        order=4,
        ndeg=15,
        kaq=[25.11, 40.0],
        z=[0.0, -6.0, -60.0, -60.5, -180.0],
        c=[3103.0, 1.0],
        topboundary='semi',
        npor=[None, None, None, None],
        hstar=-2.45,
    )
    a,b=timml_model.solve(printmat=True)
    return a, b, timml_model

def test_small():
    """
    test_small manually generates editloc tuples, injects the model and verifies whether the matrices post-injection are identical to the matrix that is being
    replicated.
    This was essentially the proof of concept of tim_editor and does not use all its functions as it predates their creation,
      for an example that uses the functions as they're supposed to,
    consider tim_editor_test_large.py
    """
    a1, b1, model1 = build_model(20, 10) #build the goal model that is being replicated

    #build two small models where one of the resistances is changed
    a_elem1, b_elem1, model_elem1 = build_model(25, 10)
    a_elem2, b_elem2, model_elem2 = build_model(20, 15)

    #generate editlocs based on the differences
    editloc1=te.generate_editloc(a1, model1, a_elem1,"editableRiver0")
    editloc2=te.generate_editloc(a1, model1, a_elem2,"editableRiver1")

    #make the model that will be injected into
    a2, b2, model2 = build_model(25, 15)

    #visualise the difference between the matrices of model1 and model2
    seaborn.heatmap(a1-a2)
    plt.title("Difference between unaltered model 1 and unaltered model 2")
    plt.show(block=False)
    plt.figure()

    a3, b3, model_small = te.build_small(editloc1[0], 20)
    seaborn.heatmap(a3)
    plt.title("First to be injected model")
    plt.show(block=False)
    plt.figure()

    a4, b4, model_small = te.build_small(editloc2[0], 10)
    seaborn.heatmap(a4)
    plt.title("Second to be injected model")
    plt.show(block=False)
    plt.figure()

    #change the matrix of model 2 by injecting the resistances of model 1 using the previously determined editlocs
    a2_edit = te.inject_res(editloc1, 20, a2)
    a2_edit = te.inject_res(editloc2, 10, a2_edit)

    #visualise the difference (there should be no difference anymore)
    seaborn.heatmap(a1-a2_edit)
    plt.title("Difference between unaltered model 1 and altered model 2")
    plt.show()
    #verify that the matrices are identical:
    print("If this prints [] the injection worked as there is no difference between the original model and the injected one: "+str(np.argwhere(a1-a2_edit)))

if __name__ == "__main__":
    test_small()