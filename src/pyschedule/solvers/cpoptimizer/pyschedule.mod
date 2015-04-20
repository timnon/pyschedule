

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
        int capacity;
}

tuple TaskResource {
	int task_id;
	int resource_id;
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
{TaskResource} TaskResources = ...;
{Precedence} Precedences = ...;
{Precedence} TightPrecedences = ...;
{CondPrecedence} CondPrecedences = ...;
{Bound} UpperBounds = ...;
{Bound} LowerBounds = ...;





dvar interval Intervals[ T in Tasks ] size T.length;
dvar interval RIntervals[ T in Tasks ][ R in Resources ] optional size T.length;

dvar sequence Resource_Seq[R in Resources] in all(T in Tasks) RIntervals[T][R] types all(T in Tasks) T.id;


execute { cp.param.FailLimit = 10000; }


minimize sum(T in Tasks ) sum( O in Objectives : O.task_id == T.id ) endOf(Intervals[T]) * O.coefficient;
//minimize max(T in Tasks ) endOf(Intervals[T]);


subject to {
  
  //forall(T in Tasks) startOf(Intervals[T]) >= j.release_time;

  forall (R in Resources)
  {
	   noOverlap(Resource_Seq[R],CondPrecedences);  
  }  

  forall( R in Resources )
  {
  	sum(T in Tasks) presenceOf(RIntervals[T][R]) <= R.capacity; // Truck capacity
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
  
  forall(T in Tasks) {
     alternative(Intervals[T], all(R in Resources : <T.id,R.id> in TaskResources ) RIntervals[T][R]); // Resource Selection
     //alternative(Intervals[T], all(R in Resources) RIntervals[T][R]); // Resource Selection
  }
 
};

execute DISPLAY {
	writeln("OBJECTIVE:"+cp.getObjValue());
}

execute {
	var f = new IloOplOutputFile("pyschedule.out");
	for (T in Tasks)
	{
		 f.writeln(Intervals[T]);
	}	
	for ( R in Resources )
	{
		f.writeln(Resource_Seq[R]);
	}	
	f.close();
}




