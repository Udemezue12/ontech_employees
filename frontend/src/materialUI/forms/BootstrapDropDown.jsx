import React from "react";
import { Controller } from "react-hook-form";

const BootstrapSelect = ({ control }) => {
  return (
    
    <div className="mb-3">
      <label htmlFor="department" className="form-label">
        Department
      </label>
      <Controller
        name="department"
        control={control}
        defaultValue=""
        render={({ field }) => (
          <select
            id="department"
            className="form-select"
            {...field}
          >
            <option value="">Select Department</option>
            <option value="Human Resources">Human Resources</option>
            <option value="Engineering">Engineering</option>
            <option value="Sales">Sales</option>
            <option value="Marketing">Marketing</option>
          </select>

        )}
      />
    </div>
  );
};

export default BootstrapSelect;
