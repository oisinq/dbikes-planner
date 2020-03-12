package io.oisin.fyp;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import java.util.List;

import androidx.recyclerview.widget.RecyclerView;
import io.oisin.fyp.model.Direction;

public class DirectionsAdapter extends
        RecyclerView.Adapter<DirectionsAdapter.ViewHolder> {

    private List<Direction> directions;

    public DirectionsAdapter(List<Direction> directions) {
        this.directions = directions;
    }

    @Override
    public DirectionsAdapter.ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        Context context = parent.getContext();
        LayoutInflater inflater = LayoutInflater.from(context);

        View contactView = inflater.inflate(R.layout.item_direction, parent, false);

        ViewHolder viewHolder = new ViewHolder(contactView);
        return viewHolder;
    }

    @Override
    public void onBindViewHolder(DirectionsAdapter.ViewHolder viewHolder, int position) {
        Direction direction = directions.get(position);

        String directionString = direction.getDirection();
        String title = directionString.substring(0, 1).toUpperCase() + directionString.substring(1) + " on " + direction.getName();

        viewHolder.directionTitleTextView.setText(title);

        if (direction.getDistance() < 95) {
            int distance = (int) Math.round(direction.getDistance()/10.0) * 10;

            viewHolder.directionSubtitleTextView.setText(distance + "m");
        } else {
            int distance = (int) Math.round(direction.getDistance()/100.0) * 100;

            viewHolder.directionSubtitleTextView.setText(distance + "m");
        }



        viewHolder.directionArrow.setImageResource(getResourceForArrow(directionString));
    }

    private int getResourceForArrow(String direction) {
        switch (direction) {
            case "bear right":
                return R.drawable.bear_right_arrow;
            case "bear left":
                return R.drawable.bear_left_arrow;
            case "turn right":
            case "sharp right":
                return R.drawable.right_arrow;
            case "turn left":
            case "sharp left":
                return R.drawable.left_arrow;
            case "straight on":
                return R.drawable.straight_ahead_arrow;
        }

        return R.drawable.straight_ahead_arrow;
    }

    @Override
    public int getItemCount() {
        return directions.size();
    }

    class ViewHolder extends RecyclerView.ViewHolder {
        TextView directionTitleTextView;
        TextView directionSubtitleTextView;
        ImageView directionArrow;

        ViewHolder(View itemView) {
            super(itemView);

            directionTitleTextView = itemView.findViewById(R.id.direction_title);
            directionSubtitleTextView = itemView.findViewById(R.id.direction_subtitle);
            directionArrow = itemView.findViewById(R.id.direction_arrow);
        }
    }
}