using NUnit.Framework;
using TMPro;
using UnityEngine;
using UnityEngine.TestTools.Utils;

public class MachineVisualEditModeTests
{
    private GameObject root;

    [SetUp]
    public void SetUp()
    {
        root = new GameObject("Lathe_01");
    }

    [TearDown]
    public void TearDown()
    {
        if (root != null)
        {
            Object.DestroyImmediate(root);
        }
    }

    [Test]
    public void UpdateState_UpdatesLabelAndRoundsQueueLength()
    {
        MeshRenderer renderer = root.AddComponent<MeshRenderer>();
        MachineVisual visual = root.AddComponent<MachineVisual>();

        GameObject labelObject = new GameObject("Label");
        labelObject.transform.SetParent(root.transform);
        TextMeshPro text = labelObject.AddComponent<TextMeshPro>();
        text.text = "Lathe 01";

        visual.bodyRenderer = renderer;
        visual.labelTMP = text;
        visual.matAmber = new Material(Shader.Find("Standard")) { color = Color.yellow };
        visual.ConfigureIdentity("Lathe 01", "Lathe");

        visual.UpdateState(0.27f, 1.6f, false, "running");

        Assert.That(visual.labelTMP.text, Does.Contain("<b>27%</b> Util"));
        Assert.That(visual.labelTMP.text, Does.Contain("Q: <b>2</b>"));
        Assert.That(visual.labelTMP.color, Is.EqualTo(Color.black));
    }
}
