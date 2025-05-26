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
    console.log("Profile updated successfully");
    return response.data;
  } catch (error) {
    console.error("Error updating profile:", error);
    throw error;
  }
};

// export const handleProfileUpdate = async (formData) => {
//   try {
//     const response = await updateUserProfile(formData);
//     console.log("Profile updated: ", response);
//   } catch (error) {
//     console.error("Failed to update profile", error);
//   }
// };
// export const handleProfileUpdate = async (formData) => {
//   // const navigate = useNavigate();
//   try {
//     const response = await updateUserProfile(formData);
//     console.log("Profile updated successfully:", response);
//     alert("Profile updated successfully!");
//     // navigate("/view/profile");
//   } catch (error) {
//     console.error("Failed to update profile:", error);
//     alert("An error occurred while updating your profile.");
//   }
// };

export const handleProfileUpdate = async (formData, navigate, setIsLoading) => {
  setIsLoading(true); // Show loading state while updating
  try {
    const response = await updateUserProfile(formData); // Call the update function
    // console.log("Profile updated successfully:", response);
    // alert("Profile updated successfully!");
    navigate("/view/profile"); // Navigate to the profile view page
  } catch (error) {
    console.error("Failed to update profile:", error);
    alert("An error occurred while updating your profile.");
  } finally {
    setIsLoading(false); // Hide loading state
  }
};
