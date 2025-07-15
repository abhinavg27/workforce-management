package com.wms.optimization.service;

import com.wms.optimization.entity.Assignment;
import com.wms.optimization.mapper.AssignmentMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
@RequiredArgsConstructor
public class AssignmentService {
    private final AssignmentMapper assignmentMapper;

    public List<Assignment> getAllAssignments() {
        return assignmentMapper.selectAllAssignments();
    }

    public Assignment getAssignmentById(Long id) {
        return assignmentMapper.selectAssignmentById(id);
    }

    public void createAssignment(Assignment assignment) {
        assignmentMapper.insertAssignment(assignment);
    }

    public void deleteAssignment(Long id) {
        assignmentMapper.deleteAssignment(id);
    }
}
