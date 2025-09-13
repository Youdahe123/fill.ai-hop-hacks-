    def adjust_last_name_position(self, coordinates):
        """
        Adjust the last name field to be positioned lower than other name fields.
        
        Args:
            coordinates (Dict[str, Tuple[float, float]]): Field coordinates
            
        Returns:
            Dict[str, Tuple[float, float]]: Adjusted coordinates
        """
        # Find last name field and move it lower
        last_name_variations = ['last_name', 'lastname', 'last name', 'surname', 'family_name']
        
        for field_name, coords in coordinates.items():
            field_lower = field_name.lower()
            if any(variation in field_lower for variation in last_name_variations):
                # Move last name lower by increasing Y coordinate
                x, y = coords
                new_y = y + 0.05  # Move down by 5% of page height
                coordinates[field_name] = (x, new_y)
                print(f"📝 Adjusted {field_name} position: ({x:.3f}, {y:.3f}) → ({x:.3f}, {new_y:.3f})")
                break
        
        return coordinates
