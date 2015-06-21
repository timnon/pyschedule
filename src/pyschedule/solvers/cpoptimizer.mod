

using CP;

tuple Objective {
	int task_id;
	float coefficient;
}

tuple Task {
	key int id;
	int length; 
}

tuple Resource {
	int id;
    int capacity_low;
    int capacity_up;
}

tuple PulseResource {
	key int id;
	int resource_size;
}

tuple TaskPulseResource {
	key int task_id;
	key int pulse_resource_id;
	int resource_size_req;
}

tuple TaskResource {
	int task_id;
	int resource_id;
	int group_id;
}

tuple TaskResourceGroup {
  	int task_id;
  	int group_id;
}

tuple Precedence {
	int left_task;
	int right_task;
	float offset;
}

tuple CondPrecedence {
	int left_task;
	int right_task;
	int offset;
}

tuple Bound {
	int task;
	float bound;
}


{Objective} Objectives = ...;
{Task} Tasks = ...;
{Resource} Resources = ...;
{PulseResource} PulseResources = ...;
{TaskPulseResource} TaskPulseResources = ...;
{TaskResource} TaskResources = ...;
{TaskResourceGroup} TaskResourceGroups = ...;
{Precedence} Precedences = ...;
{Precedence} TightPrecedences = ...;
{CondPrecedence} CondPrecedences = ...;
{Bound} UpperBounds = ...;
{Bound} LowerBounds = ...;
{Bound} FixBounds = ...;


dvar interval Intervals[ T in Tasks ] size T.length;
dvar interval RIntervals[ T in Tasks ][ R in Resources ] optional size T.length;



dvar sequence Resource_Seq[R in Resources] in all(T in Tasks) RIntervals[T][R] types all(T in Tasks) T.id;

cumulFunction ResourceFunction[TPR in TaskPulseResources] = pulse(Intervals[<TPR.task_id>],TPR.resource_size_req);



execute { cp.param.FailLimit = 10000; }


minimize sum(T in Tasks ) sum( O in Objectives : O.task_id == T.id ) endOf(Intervals[T]) * O.coefficient;
//minimize max(T in Tasks ) endOf(Intervals[T]);


subject to {


  forall (R in Resources)
  {
	   noOverlap(Resource_Seq[R],CondPrecedences);  
  }  

  forall( R in Resources )
  {
  	sum(T in Tasks) presenceOf(RIntervals[T][R]) <= R.capacity_up;
  	sum(T in Tasks) presenceOf(RIntervals[T][R]) >= R.capacity_low;
  } 

  forall (P in Precedences)
  {
     endOf(Intervals[ item(Tasks,P.left_task) ]) + P.offset <= startOf(Intervals[ item(Tasks,P.right_task) ]) ;
  	 //endBeforeStart(Jobs_Intvs[prec.job_1], Jobs_Intvs[prec.job_2]);  
  }

  forall (P in TightPrecedences)
  {
     endOf(Intervals[ item(Tasks,P.left_task) ]) + P.offset <= startOf(Intervals[ item(Tasks,P.right_task) ]) ;
     endOf(Intervals[ item(Tasks,P.left_task) ]) + P.offset >= startOf(Intervals[ item(Tasks,P.right_task) ]) ;
  }
  
  forall (B in UpperBounds)
  {
     endOf(Intervals[ item(Tasks,B.task) ]) <= B.bound;    
  }
  
  forall (B in LowerBounds)
  {
     startOf(Intervals[ item(Tasks,B.task) ]) >= B.bound;    
  }

  forall (B in FixBounds)
  {
     startOf(Intervals[ item(Tasks,B.task) ]) == B.bound;    
  }
  
  forall(T in Tasks){
        forall( TRG in TaskResourceGroups : TRG.task_id == T.id ){
               		alternative(Intervals[T], all(R in Resources : <T.id,R.id,TRG.group_id> in TaskResources ) RIntervals[T][R]); // Resource Selection        
        }
  }
  
  forall( PR in PulseResources ){
             sum( TPR in TaskPulseResources : TPR.pulse_resource_id == PR.id ) ResourceFunction[TPR] <= PR.resource_size; 
  }  
  
};

execute DISPLAY {
	writeln("OBJECTIVE:"+cp.getObjValue());
}

execute {
	var f = new IloOplOutputFile("tmp/cpoptimizer.out");
	f.writeln("INTERVALS")
	for (T in Tasks)
	{
		 f.write(T.id);f.writeln(Intervals[T]);
	}
	f.writeln("RINTERVALS")	
	for ( T in Tasks)
	{
		for (R in Resources)
		{
			f.write(T.id," ",R.id);f.writeln(RIntervals[T][R]);
		}
	}
}




