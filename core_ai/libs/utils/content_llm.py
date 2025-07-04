def json_to_readable_str(json_data, section_to_process=None):
    """
    Convert JSON outline and optionally a specific section to a readable string format for LLM consumption.
    
    Args:
        json_data (dict): The JSON outline data
        section_to_process (dict, optional): A specific section to process in detail
    
    Returns:
        str: A formatted string representation of the data
    """
    output = []
    
    # Format the main outline
    output.append("# PRESENTATION OUTLINE\n")
    output.append(f"Title: {json_data.get('topic', 'Untitled Presentation')}")
    # output.append(f"Total Sections: {json_data.get('num_sections', 0)}")
    # output.append(f"Total Slides: {json_data.get('num_slides', 0)}\n")
    
    # Process each section in the outline
    output.append("## SECTIONS OVERVIEW")
    
    for i, section in enumerate(json_data.get('sections', [])):
        section_num = i + 1
        output.append(f"\nSection {section_num}: {section.get('title', 'Untitled Section')}")
        output.append(f"Type: {section.get('section_type', 'N/A')}")
        output.append(f"Description: {section.get('description', 'No description provided')}")
        output.append(f"Slides: {section.get('estimated_slides', 1)}")
        
        # Add key points in a concise format
        # if section.get('key_points'):
        #     output.append("Key points:")
        #     for point in section['key_points']:
        #         output.append(f"- {point}")
    
    # Process the specific section in detail if provided
    if section_to_process:
        output.append("\n\n# SECTION TO DESIGN IN DETAIL")
        output.append(f"Title: {section_to_process.get('title', 'Untitled Section')}")
        output.append(f"Type: {section_to_process.get('section_type', 'N/A')}")
        output.append(f"Description: {section_to_process.get('description', 'No description provided')}")
        output.append(f"Slides: {section_to_process.get('estimated_slides', 1)}\n")
        
        output.append("Key points to include:")
        for point in section_to_process.get('key_points', ['No key points provided']):
            output.append(f"- {point}")
        
        output.append("\nGuidance for designing this section:")
        if section_to_process.get('section_type') == 'title':
            output.append("- This is the title slide that introduces the presentation")
            output.append("- Should have a clean, professional design with the title prominently displayed")
            output.append("- Include presenter information and date")
        elif section_to_process.get('section_type') == 'agenda':
            output.append("- List the main topics to be covered in the presentation")
            output.append("- Use a clear, organized layout")
        elif section_to_process.get('section_type') == 'chapter':
            output.append("- This is a main content section")
            output.append("- Consider breaking complex information into multiple slides")
            output.append("- Use visuals and bullet points where appropriate")
        elif section_to_process.get('section_type') == 'conclusion':
            output.append("- Summarize key takeaways")
            output.append("- End with a clear closing message")
        elif section_to_process.get('section_type') == 'qa':
            output.append("- Simple design focused on facilitating questions")
            output.append("- Consider including contact information for follow-up")
    
    return "\n".join(output)


# Example usage:
# 1. With just the outline
# outline_str = json_to_readable_str(json_data)

# 2. With both outline and specific section
# full_str = json_to_readable_str(json_data, json_data['sections'][0])

# 3. For processing just a specific section from the outline
# section_str = json_to_readable_str({}, json_data['sections'][0])