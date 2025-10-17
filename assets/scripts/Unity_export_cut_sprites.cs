using UnityEngine;
using UnityEditor;
using System.IO;

public class ExportAllSlices : MonoBehaviour
{
    [MenuItem("Tools/Export All Slices From Sheet")]
    static void Export()
    {
        string folderPath = "Assets/ExportedSprites";
        if (!Directory.Exists(folderPath))
            Directory.CreateDirectory(folderPath);

        // Select the master sprite sheet
        Texture2D texture = Selection.activeObject as Texture2D;
        if (texture == null)
        {
            Debug.LogError("Select a sprite sheet texture first!");
            return;
        }

        string path = AssetDatabase.GetAssetPath(texture);
        Object[] assets = AssetDatabase.LoadAllAssetsAtPath(path);

        foreach (Object asset in assets)
        {
            if (asset is Sprite sprite)
            {
                Rect rect = sprite.rect;
                Texture2D newTex = new Texture2D((int)rect.width, (int)rect.height);
                Color[] pixels = texture.GetPixels((int)rect.x, (int)rect.y, (int)rect.width, (int)rect.height);
                newTex.SetPixels(pixels);
                newTex.Apply();

                byte[] bytes = newTex.EncodeToPNG();
                string savePath = Path.Combine(folderPath, sprite.name + ".png");
                File.WriteAllBytes(savePath, bytes);
            }
        }

        AssetDatabase.Refresh();
        Debug.Log("All slices exported to " + folderPath);
    }
}
