package com.wms.optimization.mapper;


import com.wms.optimization.entity.Worker;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Mapper;
import java.util.List;

@Mapper
public interface WorkerMapper {
    List<Worker> selectAllWorkersWithDetails();
    Worker selectWorkerByIdWithDetails(@Param("workerId") String workerId);
    List<Worker> selectAllWorkers();
    void insertWorker(Worker worker);
    void insertWorkerSkill(@Param("workerId") String workerId, @Param("skillId") int skillId, @Param("skillLevel") int skillLevel, @Param("productivity") int productivity);
    void insertWorkerShift(@Param("workerId") String workerId, @Param("shiftId") int shiftId, @Param("dayOfWeek") String dayOfWeek);
    void deleteWorker(@Param("workerId") String workerId);
}
