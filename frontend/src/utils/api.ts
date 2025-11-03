const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api";

export async function loginUser(username: string, password: string) {
  try {
    const res = await fetch(`${API_URL}/login`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ username, password })
    });
    
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    
    return res.json();
  } catch (error) {
    console.error("Login error:", error);
    throw error;
  }
}

export async function uploadLog(file: File) {
  try {
    const formData = new FormData();
    formData.append("file", file);
    
    const res = await fetch(`${API_URL}/upload-log`, { 
      method: "POST", 
      body: formData 
    });
    
    // Check if response is OK
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({error: "Unknown error"}));
      throw new Error(errorData.error || `HTTP error! status: ${res.status}`);
    }
    
    const data = await res.json();
    console.log("Backend response:", data); // Debug log
    return data;
    
  } catch (error) {
    console.error("Upload error:", error);
    throw error;
  }
}