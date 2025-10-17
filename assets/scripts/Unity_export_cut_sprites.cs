using UnityEngine;
using UnityEditor;
using System.IO;

public class ExportSprites : MonoBehaviour
{
    [MenuItem("Tools/Export Sliced Sprites")]
    static void Export()
    {
        string folderPath = "Assets/ExportedSprites";
        if (!Directory.Exists(folderPath))
            Directory.CreateDirectory(folderPath);

        Object[] sprites = Selection.GetFiltered(typeof(Sprite), SelectionMode.Assets);
        foreach (Sprite sprite in sprites)
        {
            Texture2D tex = sprite.texture;
            Rect rect = sprite.rect;

            Texture2D newTex = new Texture2D((int)rect.width, (int)rect.height);
            Color[] pixels = tex.GetPixels((int)rect.x, (int)rect.y, (int)rect.width, (int)rect.height);
            newTex.SetPixels(pixels);
            newTex.Apply();

            byte[] bytes = newTex.EncodeToPNG();
            File.WriteAllBytes(Path.Combine(folderPath, sprite.name + ".png"), bytes);
        }

        AssetDatabase.Refresh();
        Debug.Log("Export complete!");
    }
}