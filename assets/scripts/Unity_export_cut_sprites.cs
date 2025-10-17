/*
 * Unity Sprite Sheet Exporter
 * Author: ChatGPT (OpenAI)
 * 
 * This script exports individual sprites from a sprite sheet in Unity.
 * It allows you to select a sprite sheet texture and automatically
 * export all slices as separate PNG files.
 * 
 * Usage:
 * 1. Import your sprite sheet into Unity
 * 2. Select the sprite sheet in the Project window
 * 3. Go to Tools > Export All Slices From Sheet
 * 4. Find exported sprites in the Assets/ExportedSprites folder
 */

using UnityEngine;
using UnityEditor;
using System.IO;

public class ExportAllSlices : MonoBehaviour
{
    // Menu item that appears in the Unity Editor under "Tools" menu
    [MenuItem("Tools/Export All Slices From Sheet")]
    static void Export()
    {
        // Define the folder path where exported sprites will be saved
        string folderPath = "Assets/ExportedSprites";
        
        // Create the folder if it doesn't exist
        if (!Directory.Exists(folderPath))
            Directory.CreateDirectory(folderPath);

        // Get the currently selected texture in the Project window (Previous comments mentioned to select the Master Sprite Sheet )
        Texture2D texture = Selection.activeObject as Texture2D;
        
        // Check if a texture is actually selected
        if (texture == null)
        {
            // Show error in console if no texture is selected
            Debug.LogError("Select a sprite sheet texture first!");
            return;
        }

        // Get the path of the selected texture
        string path = AssetDatabase.GetAssetPath(texture);
        
        // Load all assets (including sprites) at the texture path
        Object[] assets = AssetDatabase.LoadAllAssetsAtPath(path);

        // Iterate through all assets found at the texture path
        foreach (Object asset in assets)
        {
            // Check if the asset is a Sprite
            if (asset is Sprite sprite)
            {
                // Get the rectangle defining the sprite's position in the sheet
                Rect rect = sprite.rect;
                
                // Create a new texture with the sprite's dimensions
                Texture2D newTex = new Texture2D((int)rect.width, (int)rect.height);
                
                // Extract the pixels from the original texture that correspond to this sprite
                Color[] pixels = texture.GetPixels((int)rect.x, (int)rect.y, (int)rect.width, (int)rect.height);
                
                // Apply the extracted pixels to the new texture
                newTex.SetPixels(pixels);
                newTex.Apply();

                // Convert the new texture to PNG byte array
                byte[] bytes = newTex.EncodeToPNG();
                
                // Define the save path for this individual sprite
                string savePath = Path.Combine(folderPath, sprite.name + ".png");
                
                // Write the PNG data to file
                File.WriteAllBytes(savePath, bytes);
            }
        }

        // Refresh the AssetDatabase to show the newly created files in Unity
        AssetDatabase.Refresh();
        
        // Show success message in console
        Debug.Log("All slices exported to " + folderPath);
    }
}