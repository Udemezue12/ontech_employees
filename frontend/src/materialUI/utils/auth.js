import axios from "axios";
import { useNavigate } from "react-router-dom";

// export const getCurrentUserId = () => {
//   const userId = localStorage.getItem("UserId");
//   const parsedId = Number(userId);
//   return userId && !isNaN(parsedId) ? parsedId : null;
// };

// export const getCurrentUserId = () => {
//   const user = JSON.parse(localStorage.getItem("user"));
//   return user ? user.id : null; // Return the user ID, or null if it doesn't exist
// };

export const updateUserProfile = async (formData) => {
  const token = localStorage.getItem("Token");
  const userId = localStorage.getItem("UserId");
  if (!token) {
    console.error("No valid token. Please log in again.");
    window.location.href = "/login";
    return;
  }

  if (!userId) {
    console.error("No valid user ID. Cannot update profile.");
    // window.location.href = "/edit/profile";
    return;
  }

  try {
    const response = await axios.put(
      `https://ontech-systems.onrender.com/api/edit/profile/${userId}/`,
      formData,
      {
        headers: {
          Authorization: `Token ${token}`,
          "Content-Type": "multipart/form-data",
        },
      }
    );
   
    return response.data;
  } catch (error) {
    console.error("Error updating profile:", error);
    throw error;
  }
};



export const handleProfileUpdate = async (formData, navigate, setIsLoading) => {
  setIsLoading(true);
  try {
    const response = await updateUserProfile(formData); 
   
    navigate("/view/profile"); 
  } catch (error) {
    console.error("Failed to update profile:", error);
    alert("An error occurred while updating your profile.");
  } finally {
    setIsLoading(false);
  }
};
