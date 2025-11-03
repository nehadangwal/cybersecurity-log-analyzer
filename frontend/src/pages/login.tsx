import { useState } from "react";
import { useRouter } from "next/router";
import { loginUser } from "../utils/api";

export default function Login() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async () => {
    const res = await loginUser(username, password);
    if (res.status === "success") {
      router.push("/upload");
    } else {
      alert("Invalid credentials");
    }
  };

  return (
    <div className="p-10">
      <h1 className="text-2xl mb-4">Login</h1>
      <input placeholder="Username" value={username} onChange={(e)=>setUsername(e.target.value)} className="border p-2 mb-2"/>
      <input type="password" placeholder="Password" value={password} onChange={(e)=>setPassword(e.target.value)} className="border p-2 mb-2"/>
      <button onClick={handleLogin} className="bg-blue-500 text-white p-2">Login</button>
    </div>
  )
}